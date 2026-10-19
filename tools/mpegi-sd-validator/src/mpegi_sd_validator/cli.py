import argparse
import json
import os
import sys

from . import SPECIFICATION, __version__
from . import schemas
from .loader import LoadError, load
from .model import ERROR, Finding
from .validate import validate_document


def files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                for n in sorted(names):
                    if n.lower().endswith((".gltf", ".glb")):
                        yield os.path.join(root, n)
        else:
            yield p


def main(argv=None):
    ap = argparse.ArgumentParser(prog="mpegi-sd-validate", description=f"MPEG-I Scene Description - XR/3D Scene Validator: check glTF files against the MPEG-I Scene Description extensions ({SPECIFICATION}).")
    ap.add_argument("paths", nargs="*", help=".gltf or .glb files, or folders searched for them")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--summary", action="store_true", help="one line per file")
    ap.add_argument("--serve", action="store_true", help="open the dashboard on 127.0.0.1 instead of printing a report; the first path is the folder it starts on")
    ap.add_argument("--port", type=int, default=8092, help="port of the dashboard")
    ap.add_argument("--mpeg-schemas", metavar="DIR_OR_URL", help="a clone of MPEGGroup/Scene-Description, or the git URL of the repository, to read the JSON schemas from (default: MPEGI_SD_SCHEMAS, else the pinned commit, fetched into the cache folder on first use)")
    ap.add_argument("--mpeg-schemas-ref", metavar="REF", default="", help="branch, tag or commit of the repository given as a git URL with --mpeg-schemas")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    a = ap.parse_args(argv)
    try:
        if a.mpeg_schemas:
            schemas.start(a.mpeg_schemas, a.mpeg_schemas_ref)
        src = schemas.source()
    except schemas.SchemasUnavailable as e:
        print(f"mpegi-sd-validate: {e}", file=sys.stderr)
        return 2
    if not src["is_pinned"]:
        print(f"mpegi-sd-validate: the MPEG schemas are at {(src['commit'] or 'an unknown commit')[:7]}, this tool is pinned to {src['pinned'][:7]}", file=sys.stderr)
    if a.serve:
        from .dashboard import serve
        serve(a.paths[0] if a.paths else os.getcwd(), a.port)
        return 0
    if not a.paths:
        ap.error("give at least one path, or --serve")
    results, failed = [], False
    for f in files(a.paths):
        try:
            doc, binary = load(f)
            found = validate_document(doc, f, os.path.dirname(os.path.abspath(f)), binary)
        except (LoadError, OSError) as e:
            found = [Finding(f, ERROR, "LOAD", "", "", str(e))]
        errors = [x for x in found if x.severity == ERROR]
        failed |= bool(errors)
        results.append((f, found))
    if a.format == "json":
        json.dump({"specification": SPECIFICATION, "tool": __version__, "mpeg_schemas": {"url": src["url"], "commit": src["commit"]},
                   "files": [{"file": f, "findings": [x.as_dict() for x in fs]} for f, fs in results]}, sys.stdout, indent=1)
        print()
    else:
        for f, fs in results:
            ne, nw = sum(x.severity == "error" for x in fs), sum(x.severity == "warning" for x in fs)
            if a.summary or not fs:
                print(f"{'FAIL' if ne else 'ok  '} {f}  {ne} errors, {nw} warnings")
            if not a.summary:
                for x in fs:
                    print(x.line())
        n = len(results)
        bad = sum(any(x.severity == "error" for x in fs) for _, fs in results)
        print(f"\n{n} files, {n - bad} without errors, {bad} with errors")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
