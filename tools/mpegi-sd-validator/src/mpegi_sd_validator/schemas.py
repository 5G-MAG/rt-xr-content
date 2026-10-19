"""The JSON schemas of the MPEG Scene Description repository, a dependency of this tool and not part of it.

The schemas are read from a clone of https://github.com/MPEGGroup/Scene-Description, found in this order:
  1. the folder given with --mpeg-schemas or the environment variable MPEGI_SD_SCHEMAS (a clone, any commit);
  2. the cache folder, a clone at the commit this tool is pinned to (MPEG_COMMIT), made on first use with git
     (not made when MPEGI_SD_NO_FETCH is set).
The few glTF base schemas the MPEG schemas refer to (schemas/gltf) are minimal definitions of this tool, not a copy of the
Khronos files."""
import hashlib
import json
import os
import re
import subprocess
import threading
import warnings

from jsonschema import Draft7Validator

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from jsonschema import RefResolver

MPEG_URL = "https://github.com/MPEGGroup/Scene-Description.git"
MPEG_COMMIT = "5e39101aa38333248861c62404d992e10ac1f964"

BASE = "https://mpegi-sd-validator.invalid/schemas/"
_HERE = os.path.dirname(os.path.abspath(__file__))
_root = None
_default = None   # the folder chosen at start (--mpeg-schemas), to which an empty field of the page returns
_store = None
_info = None
_unusable = []


class SchemasUnavailable(Exception):
    pass


_lock = threading.Lock()
_URL = re.compile(r"^(https://|http://|git@|ssh://|file://)")


def resolve(spec, ref=""):
    """The folder of a clone of the MPEG repository named by `spec`: a folder (used as it is), or a git URL, cloned into the cache
    folder at `ref` (a branch, tag or commit; the default branch when empty). An empty `spec` is the default described above."""
    spec = (spec or "").strip()
    if not spec:
        return None
    spec = os.path.expanduser(spec)
    if os.path.isdir(spec):
        if ref:
            raise SchemasUnavailable("a branch, tag or commit goes with a git repository, not with a folder")
        return os.path.abspath(spec)
    if not _URL.match(spec):
        raise SchemasUnavailable(f"{spec} does not exist and is not a git URL")
    key = hashlib.sha1(f"{spec}@{ref}".encode()).hexdigest()[:10]
    dest = os.path.join(os.path.dirname(cache_dir()), f"Scene-Description-{key}")
    if not os.path.isdir(dest):
        if os.environ.get("MPEGI_SD_NO_FETCH"):
            raise SchemasUnavailable("fetching is forbidden (MPEGI_SD_NO_FETCH is set)")
        _fetch(dest, spec, ref)
    return dest


def use(spec, ref=""):
    """Read the schemas from `spec` (see resolve) from now on; an empty spec returns to the default."""
    with _lock:
        if not (spec or "").strip():
            set_root(_default)
        else:
            set_root(resolve(spec, ref))


def start(spec, ref=""):
    """At start: the choice of the command line, which an empty field of the page returns to."""
    global _default
    use(spec, ref)
    _default = _root


def set_root(path):
    """Use this clone of the MPEG repository (resets what was loaded)."""
    global _root, _store, _info
    _root, _store, _info = (os.path.abspath(os.path.expanduser(path)) if path else None), None, None


def _git(root, *args):
    r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def cache_dir():
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(base, "mpegi-sd-validator", "Scene-Description-" + MPEG_COMMIT[:7])


def _fetch(dest, url=MPEG_URL, ref=MPEG_COMMIT):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    try:
        cmds = [["git", "clone", "--quiet", url, tmp]] + ([["git", "-C", tmp, "checkout", "--quiet", ref]] if ref else [])
        for cmd in cmds:
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode:
                raise SchemasUnavailable(f"could not fetch the MPEG schemas ({' '.join(cmd[:3])}): {r.stderr.strip()[:300]}")
        os.replace(tmp, dest)
    finally:
        if os.path.isdir(tmp):
            subprocess.run(["rm", "-rf", tmp])


def locate():
    """The folder of the MPEG repository to read, fetching the pinned commit into the cache when needed."""
    global _root
    if _root is None:
        _root = os.environ.get("MPEGI_SD_SCHEMAS") or None
        if _root:
            _root = os.path.abspath(os.path.expanduser(_root))
    if _root:
        if not os.path.isdir(_root):
            raise SchemasUnavailable(f"the MPEG schemas folder {_root} does not exist")
        return _root
    dest = cache_dir()
    if not os.path.isdir(dest):
        if os.environ.get("MPEGI_SD_NO_FETCH"):
            raise SchemasUnavailable(_how_to())
        _fetch(dest)
    _root = dest
    return dest


def _how_to():
    return (f"the MPEG Scene Description schemas are needed and not present. Clone {MPEG_URL} (this tool is pinned to commit "
            f"{MPEG_COMMIT[:7]}) and give the folder with --mpeg-schemas or MPEGI_SD_SCHEMAS, or unset MPEGI_SD_NO_FETCH to fetch it.")


def source():
    """Where the schemas come from: the folder, its commit, and whether that is the commit this tool is pinned to."""
    global _info
    if _info is None:
        root = locate()
        commit = _git(root, "rev-parse", "HEAD")
        _info = {"url": MPEG_URL, "folder": root, "commit": commit, "pinned": MPEG_COMMIT, "is_pinned": commit == MPEG_COMMIT}
    return _info


def _load():
    global _store
    if _store is not None:
        return _store
    root = locate()
    _store = {}
    paths = [os.path.join(_HERE, "schemas", "gltf", n) for n in sorted(os.listdir(os.path.join(_HERE, "schemas", "gltf")))]
    for dp, dn, names in os.walk(root):
        dn[:] = sorted(d for d in dn if d != ".git")
        if os.path.basename(dp) == "schema":
            paths += [os.path.join(dp, n) for n in sorted(names)]
    for p in paths:
        name = os.path.basename(p)
        if not name.endswith(".schema.json"):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                _store[BASE + name] = json.load(f)
        except ValueError:
            _unusable.append(name)
    if not any(k.endswith("/MPEG_media.schema.json") for k in _store):
        _store = None
        raise SchemasUnavailable(f"{root} holds no MPEG extension schemas (folders <extension>/schema/); is it a clone of {MPEG_URL}?")
    # the interactivity schemas of the MPEG repository refer to each other as MPEG_scene_interactivity.*, while the files are
    # named MPEG_interactivity.*: both names resolve to the same schema
    for k in list(_store):
        if "/MPEG_interactivity." in k:
            _store.setdefault(k.replace("/MPEG_interactivity.", "/MPEG_scene_interactivity."), _store[k])
    return _store


def available(schema_file):
    return (BASE + schema_file) in _load()


def validator_for(schema_file):
    store = _load()
    schema = store[BASE + schema_file]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        resolver = RefResolver(base_uri=BASE + schema_file, referrer=schema, store=store)
        return Draft7Validator(schema, resolver=resolver)
