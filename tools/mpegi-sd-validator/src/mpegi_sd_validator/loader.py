import json
import struct


class LoadError(Exception):
    pass


def load(path):
    """Return (document, binary chunk or None) of a .gltf or .glb file."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] == b"glTF":
        if len(data) < 20:
            raise LoadError("the GLB header is cut short")
        _, version, length = struct.unpack_from("<III", data, 4)
        pos, doc, binary = 12, None, None
        while pos + 8 <= len(data):
            clen, ctype = struct.unpack_from("<II", data, pos)
            chunk = data[pos + 8:pos + 8 + clen]
            if ctype == 0x4E4F534A:
                doc = json.loads(chunk.decode("utf-8"))
            elif ctype == 0x004E4942 and binary is None:
                binary = chunk
            pos += 8 + clen + (-clen % 4)
        if doc is None:
            raise LoadError("the GLB has no JSON chunk")
        return doc, binary
    try:
        return json.loads(data.decode("utf-8-sig")), None
    except (ValueError, UnicodeDecodeError) as e:
        raise LoadError(f"not valid JSON: {e}")
