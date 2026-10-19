"""Checks of one glTF document: the JSON schemas of the extensions, then the rules the schemas cannot express.

Every finding names the rule, the clause of ISO/IEC 23090-14 it rests on (or says that none governs it), and the JSON
pointer of the object concerned. The rules state their own wording; no text of the specification is stored here."""
import difflib
import os
import re
from urllib.parse import unquote, urlparse

from . import schemas
from .extensions import ARRAYS, EXTENSIONS, RENAMED, SPEC
from .model import ERROR, INFO, WARNING, Finding

# format -> number of components (5.3.1.2: the number of components shall match the type of the accessor)
FORMAT_COMPONENTS = {"RED": 1, "GREEN": 1, "BLUE": 1, "DEPTH_COMPONENT": 1, "RG": 2, "RGB": 3, "BGR": 3, "RGBA": 4, "BGRA": 4}
TYPE_COMPONENTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}
COMPONENT_SIZE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
TRACKABLE = {"FLOOR": 0, "VIEWER": 1, "CONTROLLER": 2, "PLANE": 3, "MARKER_2D": 4, "MARKER_3D": 5, "MARKER_GEO": 6, "APPLICATION": 7}


# RULE: the MPEG repository governs an extension whose files were last changed after the PDF of
# ISO/IEC 23090-14; where they are older, the PDF governs (extensions.governs). Its JSON schemas check the
# structure of each extension object. Where the repository contradicts itself (a README against a schema file), neither is chosen:
# REPO-CONFLICT, information. Where the PDF governs and a schema file differs from it, the finding is SCHEMA-TEXT, information.
# An entry here is a schema error known to be one of these; its message states both sides. Anything else a schema reports is an error.
SCHEMA_DISAGREES = {
    ("MPEG_anchor", "'geoCoordinate' is a required property"):
        ("REPO-CONFLICT", "the schema file requires geoCoordinate and lists the property coordinate; the README of MPEG_anchor (Table 1, TRACKABLE_MARKER_GEO) names it coordinates"),
    ("MPEG_viewport_recommended", "'viewports' is a required property"):
        ("SCHEMA-TEXT", "the PDF governs this extension (its files date from 2023): Table 19 of clause 5.5.1.2 defines the extension object as one viewport (name, translation, rotation, type, parameters); the schema file requires a viewports array"),
}


def openxr_path(p):
    """OpenXR 1.0, 6.2 "Path name strings": only a-z 0-9 - _ . and /; one leading slash; no trailing slash; no adjacent slashes; no
    segment of periods only (two slashes separated only by periods, or only periods after the final slash)."""
    if not re.fullmatch(r"[a-z0-9_./-]+", p) or not p.startswith("/") or p.endswith("/"):
        return False
    return all(seg and seg.strip(".") for seg in p[1:].split("/"))


def _ptr(*parts):
    return "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in parts)


class Checker:
    def __init__(self, doc, filename, directory=None, binary=None):
        self.d, self.f, self.dir, self.bin = doc, filename, directory, binary
        self.out = []

    def add(self, sev, rule, clause, path, msg):
        self.out.append(Finding(self.f, sev, rule, clause, path, msg))

    # ---------------------------------------------------------------- locating the extension objects
    def ext_objects(self):
        """(place, pointer, name, value, array index) of every extension object, `place` being "root" or an array name."""
        for name, val in (self.d.get("extensions") or {}).items():
            yield "root", _ptr("extensions", name), name, val, None
        for arr in ARRAYS:
            for i, item in enumerate(self.d.get(arr) or []):
                if isinstance(item, dict):
                    for name, val in (item.get("extensions") or {}).items():
                        yield arr, _ptr(arr, i, "extensions", name), name, val, i

    # ---------------------------------------------------------------- schemas
    def schema_checks(self):
        for place, ptr, name, val, _ in list(self.ext_objects()):
            if not name.startswith("MPEG_"):
                continue
            info = EXTENSIONS.get(name)
            if info is None:
                hint = RENAMED.get(name) or (difflib.get_close_matches(name, list(EXTENSIONS), 1, 0.8) or [None])[0]
                self.add(WARNING, "EXT-002", "5.1.1", ptr, f"{name} is not an extension this document defines" + (f"; the text uses {hint}" if hint else ""))
                continue
            if info["at"] is not None and place not in info["at"]:
                self.add(ERROR, "EXT-003", info["clause"], ptr, f"{name} may only appear at {', '.join(sorted(info['at']))}, not at {place}")
            sfile = info["schema"]
            if name == "MPEG_anchor":
                sfile = "glTF.MPEG_anchor.schema.json" if place == "root" else "MPEG_anchor.schema.json"
            if not sfile or not schemas.available(sfile):
                self.add(INFO, "SCHEMA-000", info["clause"], ptr, f"no usable JSON schema for {name}: only the rules below were applied")
                continue
            v = schemas.validator_for(sfile)
            for e in sorted(v.iter_errors(val), key=lambda e: list(e.absolute_path)):
                sub = _ptr(*([p for p in ptr.strip("/").split("/")] + [str(x) for x in e.absolute_path])) if True else ptr
                if (name, e.message) in SCHEMA_DISAGREES:
                    rid, why = SCHEMA_DISAGREES[(name, e.message)]
                    self.add(INFO, rid, info["clause"], sub, why)
                    continue
                self.add(ERROR, "SCHEMA", info["clause"], sub, e.message[:240])

    # ---------------------------------------------------------------- extensionsUsed
    def declared(self):
        used = self.d.get("extensionsUsed") or []
        required = self.d.get("extensionsRequired") or []
        names = {name for _, _, name, _, _ in self.ext_objects() if name.startswith("MPEG_")}
        for n in sorted(names):
            if n not in used:
                self.add(ERROR, "EXT-001", "5.1.1", "/extensionsUsed", f"{n} is used but not listed in extensionsUsed")
        for n in required:
            if n not in used:
                self.add(ERROR, "EXT-004", "5.1.1", "/extensionsRequired", f"{n} is required but not listed in extensionsUsed")

    # ---------------------------------------------------------------- MPEG_media
    def media(self):
        m = (self.d.get("extensions") or {}).get("MPEG_media")
        if not isinstance(m, dict):
            return
        for i, item in enumerate(m.get("media") or []):
            if not isinstance(item, dict):
                continue
            p = _ptr("extensions", "MPEG_media", "media", i)
            if "autoplayGroup" in item and item.get("autoplay") is not True:
                self.add(ERROR, "MEDIA-001", "5.2.1.2", p + "/autoplayGroup", "autoplayGroup is only allowed when autoplay is true")
            if "autoplayGroup" in item and isinstance(item["autoplayGroup"], bool):
                self.add(ERROR, "MEDIA-002", "5.2.1.2", p + "/autoplayGroup", "autoplayGroup is an integer, not a boolean")
            if item.get("autoplay") is True and "startTime" in item:
                self.add(WARNING, "MEDIA-003", "5.2.1.2", p + "/startTime", "startTime shall not be present when autoplay is true, or the client ignores it")
            so, eo = item.get("startTimeOffset", 0), item.get("endTimeOffset")
            if isinstance(eo, (int, float)) and isinstance(so, (int, float)) and not isinstance(eo, bool) and eo <= so:
                self.add(WARNING, "MEDIA-004", "5.2.1.2", p + "/endTimeOffset", f"endTimeOffset {eo} is not after startTimeOffset {so}: the range is empty (omit endTimeOffset to play to the end of the source)")

    # ---------------------------------------------------------------- buffers, accessors, textures
    def _buffer_has_circular(self, bi):
        b = (self.d.get("buffers") or [])
        return 0 <= bi < len(b) and isinstance(b[bi], dict) and "MPEG_buffer_circular" in (b[bi].get("extensions") or {})

    def buffers(self):
        medias = ((self.d.get("extensions") or {}).get("MPEG_media") or {}).get("media") or []
        views = self.d.get("bufferViews") or []
        for bi, b in enumerate(self.d.get("buffers") or []):
            ext = (b.get("extensions") or {}).get("MPEG_buffer_circular") if isinstance(b, dict) else None
            if not isinstance(ext, dict):
                continue
            p = _ptr("buffers", bi)
            if "uri" in b:
                self.add(ERROR, "BUF-001", "5.2.3.1", p + "/uri", "a buffer with MPEG_buffer_circular shall not have a uri")
            mi = ext.get("media")
            if isinstance(mi, int):
                if not 0 <= mi < len(medias):
                    self.add(ERROR, "BUF-002", "5.2.3.2", p + "/extensions/MPEG_buffer_circular/media", f"media {mi} is not an entry of MPEG_media ({len(medias)} entries)")
                else:
                    alts = medias[mi].get("alternatives") or []
                    tr = ext.get("tracks")
                    if tr and alts:
                        for a, alt in enumerate(alts):
                            n = len(alt.get("tracks") or [])
                            if n and any(isinstance(t, int) and t >= n for t in tr):
                                self.add(ERROR, "BUF-003", "5.2.3.2", p + "/extensions/MPEG_buffer_circular/tracks", f"a listed track is not in alternative {a} of media {mi} ({n} tracks)")
            # the byteLength shall indicate the maximum size needed: the frames of count times the extent of the views
            count = ext.get("count", 2)
            frame = 0
            for v in views:
                if isinstance(v, dict) and v.get("buffer") == bi:
                    frame = max(frame, v.get("byteOffset", 0) + v.get("byteLength", 0))
            if isinstance(count, int) and frame and isinstance(b.get("byteLength"), int) and b["byteLength"] < frame * count:
                self.add(WARNING, "BUF-004", "5.2.3.1", p + "/byteLength",
                         f"byteLength {b['byteLength']} holds {b['byteLength'] / frame:.2f} frames of {frame} bytes; count is {count}")

    def accessors(self):
        views = self.d.get("bufferViews") or []
        headers = {}  # buffer -> whether each of its timed accessors has a header bufferView
        for ai, a in enumerate(self.d.get("accessors") or []):
            if not isinstance(a, dict):
                continue
            ext = (a.get("extensions") or {}).get("MPEG_accessor_timed")
            p = _ptr("accessors", ai)
            bv = a.get("bufferView")
            buf = views[bv].get("buffer") if isinstance(bv, int) and 0 <= bv < len(views) and isinstance(views[bv], dict) else None
            if not isinstance(ext, dict):
                continue
            if buf is not None and not self._buffer_has_circular(buf):
                self.add(ERROR, "ACC-005", "5.2.2.1", p, "an accessor with MPEG_accessor_timed shall only point to a buffer with MPEG_buffer_circular")
            ebv = ext.get("bufferView")
            if buf is not None:
                headers.setdefault(buf, set()).add(ebv is not None)
            if ebv is None:
                if ext.get("immutable") is not True:
                    self.add(ERROR, "ACC-002", "5.2.2.2", p + "/extensions/MPEG_accessor_timed", "without a bufferView the immutable flag shall be present and true")
            elif not (isinstance(ebv, int) and 0 <= ebv < len(views)):
                self.add(ERROR, "ACC-003", "5.2.2.2", p + "/extensions/MPEG_accessor_timed/bufferView", f"bufferView {ebv} does not exist")
            elif buf is not None and views[ebv].get("buffer") != buf:
                self.add(ERROR, "ACC-004", "5.2.2.2", p + "/extensions/MPEG_accessor_timed/bufferView", "the header bufferView shall point to the same buffer as the bufferView of the accessor")
        for buf, kinds in sorted(headers.items()):
            if len(kinds) > 1:
                self.add(ERROR, "ACC-006", "5.2.2.3", _ptr("buffers", buf), "a buffer shall not mix accessors that have a timed accessor information header with accessors that do not")

    def textures(self):
        accs = self.d.get("accessors") or []
        for ti, t in enumerate(self.d.get("textures") or []):
            ext = (t.get("extensions") or {}).get("MPEG_texture_video") if isinstance(t, dict) else None
            if not isinstance(ext, dict):
                continue
            p = _ptr("textures", ti, "extensions", "MPEG_texture_video")
            ai = ext.get("accessor")
            if not (isinstance(ai, int) and 0 <= ai < len(accs)):
                self.add(ERROR, "TEX-001", "5.3.1.2", p + "/accessor", f"accessor {ai} does not exist")
                continue
            a = accs[ai]
            if "MPEG_accessor_timed" not in (a.get("extensions") or {}):
                self.add(ERROR, "TEX-002", "5.3.1.2", p + "/accessor", "the accessor shall have the MPEG_accessor_timed extension")
            fmt = ext.get("format", "RGB")
            if fmt in FORMAT_COMPONENTS and a.get("type") in TYPE_COMPONENTS and FORMAT_COMPONENTS[fmt] != TYPE_COMPONENTS[a["type"]]:
                self.add(ERROR, "TEX-003", "5.3.1.2", p + "/format", f"format {fmt} has {FORMAT_COMPONENTS[fmt]} components but the accessor type {a['type']} has {TYPE_COMPONENTS[a['type']]}")

    # ---------------------------------------------------------------- accessors of a given format
    def accessor_format(self, ptr, index, component, typ, rule, clause, label):
        accs = self.d.get("accessors") or []
        if not (isinstance(index, int) and 0 <= index < len(accs)) or not isinstance(accs[index], dict):
            return
        a = accs[index]
        if a.get("componentType") != component or a.get("type") != typ:
            self.add(ERROR, rule, clause, ptr, f"the accessor {index} has componentType {a.get('componentType')} and type {a.get('type')}; {label}")

    def accessor_formats(self):
        for place, ptr, name, val, _ in self.ext_objects():
            if not isinstance(val, dict):
                continue
            if name == "MPEG_viewport_recommended":
                for here, v in [(ptr, val)] + [(f"{ptr}/viewports/{i}", x) for i, x in enumerate(val.get("viewports") or []) if isinstance(x, dict)]:
                    self.accessor_format(here + "/translation", v.get("translation"), 5126, "VEC3", "VIEW-001", "5.5.1.2", "the componentType shall be FLOAT (5126) and the type VEC3")
                    self.accessor_format(here + "/rotation", v.get("rotation"), 5126, "VEC4", "VIEW-002", "5.5.1.2", "the componentType shall be FLOAT (5126) and the type VEC4")
                    self.accessor_format(here + "/parameters", v.get("parameters"), 5126, "VEC4", "VIEW-003", "5.5.1.2", "the componentType shall be FLOAT (5126) and the type VEC4")
            elif name == "MPEG_animation_timing":
                self.accessor_format(ptr + "/accessor", val.get("accessor"), 5120, "SCALAR", "ANIM-001", "5.5.2.2", "the componentType shall be BYTE (5120) and the type SCALAR")
            elif name == "MPEG_mesh_linking":
                accs = self.d.get("accessors") or []
                ci = val.get("correspondence")
                if isinstance(ci, int) and 0 <= ci < len(accs) and isinstance(accs[ci], dict) and accs[ci].get("type") != "SCALAR":
                    self.add(ERROR, "MESH-001", "5.3.2.2", ptr + "/correspondence", f"the accessor {ci} has type {accs[ci].get('type')}; the type shall be SCALAR")
                self.accessor_format(ptr + "/pose", val.get("pose"), 5126, "MAT4", "MESH-002", "5.3.2.2", "the componentType shall be FLOAT (5126) and the type MAT4")
                self.accessor_format(ptr + "/weights", val.get("weights"), 5126, "SCALAR", "MESH-003", "5.3.2.2", "the componentType shall be FLOAT (5126) and the type SCALAR")
                mi = val.get("mesh")
                if isinstance(mi, int) and not 0 <= mi < len(self.d.get("meshes") or []):
                    self.add(ERROR, "MESH-004", "5.3.2.2", ptr + "/mesh", f"mesh {mi} is not an item of the meshes array")

    # ---------------------------------------------------------------- audio
    def audio(self):
        for place, ptr, name, val, _ in self.ext_objects():
            if name != "MPEG_audio_spatial" or not isinstance(val, dict):
                continue
            if place == "nodes" and not ("sources" in val or "listener" in val or "source" in val):
                self.add(ERROR, "AUD-001", "5.4.1.1", ptr, "on a node, either sources or listener shall be present")
            if place == "root" and not val.get("reverbs") and "reverb" not in val:
                self.add(ERROR, "AUD-002", "5.4.1.1", ptr, "at the glTF file level the reverb property shall be present")
            for si, src in enumerate(val.get("sources") or []):
                if not isinstance(src, dict):
                    continue
                here = f"{ptr}/sources/{si}"
                feed, gain = src.get("reverbFeed"), src.get("reverbFeedGain")
                if isinstance(feed, list) and isinstance(gain, list) and len(feed) != len(gain):
                    self.add(ERROR, "AUD-003", "5.4.1.2", here + "/reverbFeedGain", f"reverbFeedGain has {len(gain)} elements, reverbFeed has {len(feed)}")
                if src.get("isCluster") is True and "clusterProperties" not in src:
                    self.add(ERROR, "AUD-004", "5.4.1.2", here, "clusterProperties shall be defined when isCluster is true")
                if src.get("type") == "HOA" and "referenceDistance" in src:
                    self.add(ERROR, "AUD-005", "5.4.1.2", here + "/referenceDistance", "referenceDistance shall not be present when type is HOA")

    # ---------------------------------------------------------------- anchors
    def anchors(self):
        root = (self.d.get("extensions") or {}).get("MPEG_anchor")
        refs = [(pl, ptr, v) for pl, ptr, n, v, _ in self.ext_objects() if n == "MPEG_anchor" and pl in ("scenes", "nodes")]
        scene_level = any(pl == "scenes" for pl, _, _ in refs)
        node_level = any(pl == "nodes" for pl, _, _ in refs)
        if scene_level and node_level:
            self.add(ERROR, "ANC-001", "8.1.3", "/", "MPEG_anchor shall not be present at scene level and node level in the same file")
        if refs and not isinstance(root, dict):
            self.add(ERROR, "ANC-002", "8.1.2", "/extensions", "the trackables and anchors shall be defined in an MPEG_anchor extension at the glTF file level")
            return
        if not isinstance(root, dict):
            return
        anchors, tracks = root.get("anchors") or [], root.get("trackables") or []
        nodes = self.d.get("nodes") or []
        for pl, ptr, v in refs:
            ai = v.get("anchor") if isinstance(v, dict) else None
            if isinstance(ai, int) and not 0 <= ai < len(anchors):
                self.add(ERROR, "ANC-003", "8.1.2", ptr + "/anchor", f"anchor {ai} is not an item of the anchors array ({len(anchors)} items)")
        base = _ptr("extensions", "MPEG_anchor")
        for i, a in enumerate(anchors):
            if isinstance(a, dict) and isinstance(a.get("trackable"), int) and not 0 <= a["trackable"] < len(tracks):
                self.add(ERROR, "ANC-004", "8.1.2", f"{base}/anchors/{i}/trackable", f"trackable {a['trackable']} is not an item of the trackables array ({len(tracks)} items)")
        for i, t in enumerate(tracks):
            if not isinstance(t, dict):
                continue
            tp, here = t.get("type"), f"{base}/trackables/{i}"
            need = {2: "path", 3: "geometricConstraint", 4: "markerNode", 5: "markerNode", 6: "coordinates", 7: "trackableId"}.get(tp)
            if need and need not in t:
                if need == "coordinates" and "coordinate" in t:
                    self.add(INFO, "REPO-CONFLICT", "8.1.2", here + "/coordinate", "repository conflict: the README of MPEG_anchor names this property coordinates; its schema file names it coordinate")
                else:
                    self.add(ERROR, "ANC-005", "8.1.2", here, f"a trackable of type {tp} shall have {need}")
            if tp in (4, 5) and isinstance(t.get("markerNode"), int) and not 0 <= t["markerNode"] < len(nodes):
                self.add(ERROR, "ANC-006", "8.1.2", here + "/markerNode", f"markerNode {t['markerNode']} is not a node")
            c = t.get("coordinates")
            if tp == 6 and isinstance(c, list) and len(c) == 3 and all(isinstance(x, (int, float)) for x in c):
                if not -180.0 <= c[0] <= 180.0:
                    self.add(ERROR, "ANC-007", "8.1.2", here + "/coordinates/0", f"the first value is the longitude and lies in -180 to 180 degrees; got {c[0]}")
                if not -90.0 <= c[1] <= 90.0:
                    self.add(ERROR, "ANC-008", "8.1.2", here + "/coordinates/1", f"the second value is the latitude and lies in -90 to 90 degrees; got {c[1]}")

    # ---------------------------------------------------------------- interactivity
    def interactivity(self):
        nodes = self.d.get("nodes") or []
        for pl, ptr, n, v, _ in self.ext_objects():
            if n != "MPEG_scene_interactivity" or not isinstance(v, dict):
                continue
            trig, act = v.get("triggers") or [], v.get("actions") or []
            for bi, b in enumerate(v.get("behaviors") or []):
                if not isinstance(b, dict):
                    continue
                for key, pool, label in (("triggers", trig, "trigger"), ("actions", act, "action")):
                    for x in b.get(key) or []:
                        if isinstance(x, int) and not 0 <= x < len(pool):
                            self.add(ERROR, "INT-001", "8.2.2.1", f"{ptr}/behaviors/{bi}/{key}", f"{label} {x} is not an item of the {key} array ({len(pool)} items)")
            for key, items in (("triggers", trig), ("actions", act)):
                for i, it in enumerate(items):
                    path = it.get("userInputDescription") if isinstance(it, dict) else None
                    if isinstance(path, str) and not openxr_path(path):
                        self.add(ERROR, "INT-003", "8.2.2.1", f"{ptr}/{key}/{i}/userInputDescription", f"{path!r} is not an OpenXR path name string (lower case a-z, 0-9, - _ . and /, one leading /, no trailing /, no empty or dot-only segment)")
                    for ni in (it.get("nodes") or []) if isinstance(it, dict) else []:
                        if isinstance(ni, int) and not 0 <= ni < len(nodes):
                            self.add(ERROR, "INT-002", "8.2.2.1", f"{ptr}/{key}/{i}/nodes", f"node {ni} does not exist")

    # ---------------------------------------------------------------- the glTF base the extensions build on
    def gltf_base(self):
        views = self.d.get("bufferViews") or []
        for bi, b in enumerate(self.d.get("buffers") or []):
            uri = b.get("uri") if isinstance(b, dict) else None
            if not uri or uri.startswith("data:") or self.dir is None:
                continue
            u = urlparse(uri)
            if u.scheme in ("http", "https"):
                continue
            path = os.path.join(self.dir, unquote(u.path))
            if not os.path.exists(path):
                self.add(ERROR, "GLTF-001", "", _ptr("buffers", bi, "uri"), f"the buffer file {uri} does not exist")
            elif isinstance(b.get("byteLength"), int) and os.path.getsize(path) < b["byteLength"]:
                self.add(ERROR, "GLTF-001", "glTF 2.0, 3.6.1.1", _ptr("buffers", bi, "uri"),
                         f"the file {uri} has {os.path.getsize(path)} bytes, fewer than the buffer byteLength {b['byteLength']}")
        for ai, a in enumerate(self.d.get("accessors") or []):
            if not isinstance(a, dict) or not isinstance(a.get("bufferView"), int) or not 0 <= a["bufferView"] < len(views):
                continue
            bv = views[a["bufferView"]]
            comp, typ, cnt = COMPONENT_SIZE.get(a.get("componentType")), TYPE_COMPONENTS.get(a.get("type")), a.get("count")
            if comp and typ and isinstance(cnt, int) and cnt > 0 and isinstance(bv.get("byteLength"), int):
                stride = bv.get("byteStride") or comp * typ
                need = a.get("byteOffset", 0) + stride * (cnt - 1) + comp * typ
                if need > bv["byteLength"]:
                    self.add(ERROR, "GLTF-002", "glTF 2.0, 3.6.2.4", _ptr("accessors", ai), f"the accessor needs {need} bytes of its bufferView, which has {bv['byteLength']}")

    def run(self):
        self.schema_checks()
        self.declared()
        self.media()
        self.buffers()
        self.accessors()
        self.textures()
        self.audio()
        self.accessor_formats()
        self.anchors()
        self.interactivity()
        self.gltf_base()
        return self.out


def validate_document(doc, filename="<memory>", directory=None, binary=None):
    return Checker(doc, filename, directory, binary).run()
