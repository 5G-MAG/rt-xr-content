import json
import os
import warnings

from jsonschema import Draft7Validator

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from jsonschema import RefResolver

BASE = "https://mpegi-sd-validator.invalid/schemas/"
_HERE = os.path.dirname(os.path.abspath(__file__))
_store = None
_unusable = []


def _load():
    global _store
    if _store is not None:
        return _store
    _store = {}
    for sub in ("gltf", "mpeg"):
        d = os.path.join(_HERE, "schemas", sub)
        for name in sorted(os.listdir(d)):
            if not name.endswith(".schema.json"):
                continue
            try:
                with open(os.path.join(d, name), encoding="utf-8") as f:
                    _store[BASE + name] = json.load(f)
            except ValueError:
                _unusable.append(name)
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
