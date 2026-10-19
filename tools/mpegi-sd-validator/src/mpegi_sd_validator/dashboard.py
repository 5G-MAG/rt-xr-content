"""Local web page for the validator: runs it on a folder, or on a git URL at a branch, tag or commit, and shows the
result per scene and per rule. Standard library only; serves on 127.0.0.1."""
import json
import os
import re
import subprocess
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import SPECIFICATION, __version__
from . import schemas
from .loader import LoadError, load
from .model import ERROR, Finding
from .validate import validate_document

STATIC = os.path.join(os.path.dirname(__file__), "static")
CACHE = os.path.join(tempfile.gettempdir(), "mpegi-sd-validator-src")


def rules():
    """The rule reference: src/mpegi_sd_validator/rules.json, each rule with the sentence that obliges it."""
    with open(os.path.join(os.path.dirname(__file__), "rules.json"), encoding="utf-8") as f:
        return json.load(f)["rules"]


def resolve(source, ref):
    """A local folder as given, or a clone of a git URL at ref (shallow, cached by URL and ref)."""
    source = os.path.expanduser(source.strip())
    if os.path.isdir(source):
        return source, _head(source)
    if not re.match(r"^(https://|git@|ssh://)", source):
        raise ValueError(f"{source} is neither a folder nor a git URL")
    dest = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9]+", "_", source + "@" + (ref or "HEAD")))
    if os.path.isdir(dest):
        subprocess.run(["rm", "-rf", dest], check=True)
    os.makedirs(CACHE, exist_ok=True)
    cmd = ["git", "clone", "--quiet", "--depth", "1"] + (["--branch", ref] if ref else []) + [source, dest]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:  # a commit id cannot be given to --branch
        subprocess.run(["rm", "-rf", dest])
        subprocess.run(["git", "clone", "--quiet", source, dest], check=True, capture_output=True)
        subprocess.run(["git", "-C", dest, "checkout", "--quiet", ref], check=True, capture_output=True)
    return dest, _head(dest)


def _head(d):
    r = subprocess.run(["git", "-C", d, "log", "-1", "--format=%h %s"], capture_output=True, text=True)
    b = subprocess.run(["git", "-C", d, "branch", "--show-current"], capture_output=True, text=True)
    return (b.stdout.strip() + " " + r.stdout.strip()).strip() if r.returncode == 0 else ""


def scene_files(root):
    found = []
    for dp, dn, names in os.walk(root):
        dn[:] = sorted(d for d in dn if not d.startswith("."))
        found += [os.path.join(dp, n) for n in sorted(names) if n.lower().endswith((".gltf", ".glb"))]
    return found


def run(source, ref="", progress=None, schemas_spec="", schemas_ref=""):
    """progress(phase, done, total, current) is called before each step."""
    note = progress or (lambda *a: None)
    if schemas_spec.strip():
        note("Fetching the MPEG schemas", 0, 0, "")
        schemas.use(schemas_spec, schemas_ref)
    else:
        schemas.use("")
    note("Fetching the source" if re.match(r"^(https://|git@|ssh://)", source.strip()) else "Reading the folder", 0, 0, "")
    root, head = resolve(source, ref)
    paths = scene_files(root)
    out = []
    for i, f in enumerate(paths):
        rel = os.path.relpath(f, root)
        note("Validating", i, len(paths), rel)
        used = []
        try:
            doc, binary = load(f)
            used = [e for e in doc.get("extensionsUsed", []) if e.startswith("MPEG_")]
            found = validate_document(doc, f, os.path.dirname(f), binary)
        except (LoadError, OSError) as e:
            found = [Finding(f, ERROR, "LOAD", "", "", str(e))]
        out.append({"file": rel, "extensions": used, "findings": [dict(x.as_dict(), file=rel) for x in found]})
    note("Done", len(paths), len(paths), "")
    return {"specification": SPECIFICATION, "tool": __version__, "mpeg_schemas": {"url": schemas.source()["url"], "commit": schemas.source()["commit"]},
            "source": source, "ref": ref, "head": head, "files": out}


JOBS = {}


def start_job(source, ref, schemas_spec="", schemas_ref=""):
    """Run in a thread; the page polls /api/job. `beat` is the time of the last step, so a stalled run can be told from a slow one."""
    jid = uuid.uuid4().hex[:8]
    job = JOBS[jid] = {"phase": "Starting", "done": 0, "total": 0, "current": "", "started": time.time(), "beat": time.time(),
                       "finished": False, "error": None, "result": None}

    def progress(phase, done, total, current):
        job.update(phase=phase, done=done, total=total, current=current, beat=time.time())

    def work():
        try:
            job["result"] = run(source, ref, progress, schemas_spec, schemas_ref)
        except Exception as e:  # shown on the page
            job["error"] = str(e)
        job["finished"] = True
        job["beat"] = time.time()
    threading.Thread(target=work, daemon=True).start()
    return jid


def report_md(r):
    n = len(r["files"])
    bad = [f for f in r["files"] if any(x["severity"] == ERROR for x in f["findings"])]
    L = [f"# MPEG-I Scene Description check", "",
         f"- Specification: {r['specification']}", f"- Tool: mpegi-sd-validator {r['tool']}",
         f"- MPEG schemas: {r['mpeg_schemas']['url']} at {(r['mpeg_schemas']['commit'] or '')[:7]}",
         f"- Source: {r['source']}" + (f" at {r['ref']}" if r["ref"] else "") + (f" ({r['head']})" if r["head"] else ""),
         f"- Result: {n} files, {n - len(bad)} without errors, {len(bad)} with errors", ""]
    for f in r["files"]:
        if not f["findings"]:
            continue
        L += [f"## {f['file']}", ""]
        for x in f["findings"]:
            cl = f" (clause {x['clause']})" if x["clause"] else ""
            L.append(f"- **{x['severity']}** `{x['rule']}`{cl} at `{x['path'] or '/'}`: {x['message']}")
        L.append("")
    L += ["Reproduce: `mpegi-sd-validate <folder> --format json`", ""]
    return "\n".join(L)


def make_handler(default_source):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body, ctype):
            b = body.encode() if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            u = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            if u.path == "/":
                return self.send(200, open(os.path.join(STATIC, "index.html"), "rb").read(), "text/html; charset=utf-8")
            if u.path.startswith("/static/"):
                f = os.path.realpath(os.path.join(STATIC, u.path[len("/static/"):]))
                if f.startswith(STATIC + os.sep) and os.path.isfile(f):
                    ct = {".css": "text/css", ".png": "image/png", ".js": "text/javascript"}.get(os.path.splitext(f)[1], "application/octet-stream")
                    return self.send(200, open(f, "rb").read(), ct)
                return self.send(404, "not found", "text/plain")
            if u.path == "/api/config":
                return self.send(200, json.dumps({"source": default_source, "specification": SPECIFICATION, "tool": __version__, "schemas": schemas.source()}), "application/json")
            if u.path == "/api/rules":
                return self.send(200, json.dumps(rules()), "application/json")
            if u.path == "/api/start":
                return self.send(200, json.dumps({"id": start_job(q.get("source") or default_source, q.get("ref", ""), q.get("schemas", ""), q.get("schemas_ref", ""))}), "application/json")
            if u.path == "/api/job":
                j = JOBS.get(q.get("id", ""))
                if j is None:
                    return self.send(404, json.dumps({"error": "unknown job"}), "application/json")
                now = time.time()
                view = {k: v for k, v in j.items() if k not in ("result",)}
                view.update(elapsed=round(now - j["started"], 1), idle=round(now - j["beat"], 1))
                if j["finished"] and not j["error"]:
                    view["result"] = j["result"]
                return self.send(200, json.dumps(view), "application/json")
            if u.path in ("/api/run", "/report.md", "/report.json"):
                try:
                    r = run(q.get("source") or default_source, q.get("ref", ""), None, q.get("schemas", ""), q.get("schemas_ref", ""))
                except Exception as e:  # shown on the page
                    return self.send(400, json.dumps({"error": str(e)}), "application/json")
                if u.path == "/report.md":
                    return self.send(200, report_md(r), "text/markdown; charset=utf-8")
                return self.send(200, json.dumps(r), "application/json")
            self.send(404, "not found", "text/plain")
    return H


def serve(source, port=8092):
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(source))
    print(f"mpegi-sd-validator dashboard on http://127.0.0.1:{port}/  (source: {source})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
