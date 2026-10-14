import copy
import json
import os

import pytest

from mpegi_sd_validator.cli import main
from mpegi_sd_validator.validate import validate_document


def good():
    """A small scene that uses MPEG_media, a circular buffer, a timed accessor, a video texture and a floor anchor."""
    return {
        "asset": {"version": "2.0"},
        "extensionsUsed": ["MPEG_media", "MPEG_buffer_circular", "MPEG_accessor_timed", "MPEG_texture_video", "MPEG_anchor"],
        "extensions": {
            "MPEG_media": {"media": [{"name": "v", "autoplay": True, "loop": True,
                                      "alternatives": [{"mimeType": "video/mp4", "uri": "v.mp4"}]}]},
            "MPEG_anchor": {"trackables": [{"type": 0}], "anchors": [{"trackable": 0, "requiresAnchoring": True}]},
        },
        "scenes": [{"nodes": [0]}],
        "nodes": [{"extensions": {"MPEG_anchor": {"anchor": 0}}}],
        "buffers": [{"byteLength": 2 * 12, "extensions": {"MPEG_buffer_circular": {"count": 2, "media": 0}}}],
        "bufferViews": [{"buffer": 0, "byteLength": 12}],
        "accessors": [{"bufferView": 0, "componentType": 5121, "count": 4, "type": "VEC3",
                       "extensions": {"MPEG_accessor_timed": {"immutable": True, "suggestedUpdateRate": 24}}}],
        "textures": [{"extensions": {"MPEG_texture_video": {"accessor": 0, "width": 2, "height": 2, "format": "RGB"}}}],
    }


def rules(doc):
    return {(f.rule, f.severity) for f in validate_document(doc)}


def test_good_scene_has_no_errors():
    assert not [f for f in validate_document(good()) if f.severity == "error"]


def case(mutate, rule):
    d = good()
    mutate(d)
    assert (rule, "error") in rules(d), [f.line() for f in validate_document(d)]


def test_extension_not_listed():
    case(lambda d: d["extensionsUsed"].remove("MPEG_anchor"), "EXT-001")


def test_unknown_mpeg_extension_with_hint():
    d = good()
    d["nodes"][0]["extensions"]["MPEG_avatar"] = {}
    d["extensionsUsed"].append("MPEG_avatar")
    f = [x for x in validate_document(d) if x.rule == "EXT-002"]
    assert f and "MPEG_node_avatar" in f[0].message


def test_media_not_at_root():
    case(lambda d: d["nodes"][0]["extensions"].update({"MPEG_media": d["extensions"]["MPEG_media"]}), "EXT-003")


def test_autoplay_group_needs_autoplay_true():
    case(lambda d: d["extensions"]["MPEG_media"]["media"][0].update({"autoplay": False, "autoplayGroup": 1}), "MEDIA-001")


def test_autoplay_group_is_integer():
    case(lambda d: d["extensions"]["MPEG_media"]["media"][0].update({"autoplayGroup": False}), "MEDIA-002")


def test_circular_buffer_has_no_uri():
    case(lambda d: d["buffers"][0].update({"uri": "x.bin"}), "BUF-001")


def test_circular_buffer_media_index():
    case(lambda d: d["buffers"][0]["extensions"]["MPEG_buffer_circular"].update({"media": 3}), "BUF-002")


def test_circular_buffer_holds_count_frames():
    case(lambda d: d["buffers"][0].update({"byteLength": 12}), "BUF-004")


def test_timed_accessor_needs_extension():
    case(lambda d: d["accessors"][0]["extensions"].pop("MPEG_accessor_timed"), "ACC-001")


def test_timed_accessor_without_header_is_immutable():
    case(lambda d: d["accessors"][0]["extensions"]["MPEG_accessor_timed"].pop("immutable"), "ACC-002")


def test_video_texture_components_match_accessor_type():
    case(lambda d: d["textures"][0]["extensions"]["MPEG_texture_video"].update({"format": "RGBA"}), "TEX-003")


def test_video_texture_picture_size_matches_accessor_count():
    case(lambda d: d["textures"][0]["extensions"]["MPEG_texture_video"].update({"width": 3}), "TEX-004")


def test_anchor_at_scene_and_node_level():
    case(lambda d: d["scenes"][0].update({"extensions": {"MPEG_anchor": {"anchor": 0}}}), "ANC-001")


def test_anchor_index_out_of_range():
    case(lambda d: d["nodes"][0]["extensions"]["MPEG_anchor"].update({"anchor": 5}), "ANC-003")


def test_geo_longitude_first():
    def m(d):
        d["extensions"]["MPEG_anchor"]["trackables"][0] = {"type": 6, "coordinates": [48.1, -1.6, 164.0]}
        d["extensions"]["MPEG_anchor"]["trackables"].append({"type": 6, "coordinates": [10.0, 120.0, 0.0]})
        d["extensions"]["MPEG_anchor"]["anchors"].append({"trackable": 1, "requiresAnchoring": True})
    case(m, "ANC-008")


def test_missing_trackable_property():
    case(lambda d: d["extensions"]["MPEG_anchor"]["trackables"].append({"type": 7}), "ANC-005")


def test_scene_interactivity_needs_triggers_actions_behaviors():
    case(lambda d: d["scenes"][0].update({"extensions": {"MPEG_scene_interactivity": {"actions": []}}}), "SCHEMA")


def test_accessor_must_fit_buffer_view():
    case(lambda d: d["accessors"][0].update({"count": 40}), "GLTF-002")


def test_buffer_file_shorter_than_byte_length(tmp_path):
    d = good()
    d["buffers"].append({"uri": "g.bin", "byteLength": 140})
    (tmp_path / "g.bin").write_bytes(b"\0" * 128)
    found = validate_document(d, "x.gltf", str(tmp_path))
    assert any(f.rule == "GLTF-001" for f in found)


def test_cli_exit_code_and_json(tmp_path, capsys):
    ok, bad = good(), good()
    bad["extensionsUsed"].remove("MPEG_anchor")
    (tmp_path / "ok.gltf").write_text(json.dumps(ok))
    (tmp_path / "bad.gltf").write_text(json.dumps(bad))
    assert main([str(tmp_path / "ok.gltf")]) == 0
    capsys.readouterr()
    assert main([str(tmp_path), "--format", "json"]) == 1
    out = json.loads(capsys.readouterr().out)
    by_file = {os.path.basename(f["file"]): f["findings"] for f in out["files"]}
    assert not by_file["ok.gltf"]
    assert by_file["bad.gltf"][0]["rule"] == "EXT-001" and by_file["bad.gltf"][0]["clause"] == "5.1.1"


def test_glb_is_read(tmp_path):
    import struct
    payload = json.dumps(good()).encode()
    payload += b" " * (-len(payload) % 4)
    glb = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(payload)) + struct.pack("<II", len(payload), 0x4E4F534A) + payload
    (tmp_path / "s.glb").write_bytes(glb)
    assert main([str(tmp_path / "s.glb")]) == 0


def test_rules_reference_matches_the_code():
    import os, re
    from mpegi_sd_validator import dashboard
    src = open(os.path.join(os.path.dirname(dashboard.__file__), "validate.py"), encoding="utf-8").read()
    raised = set(re.findall(r'self\.add\((?:ERROR|WARNING|INFO),\s*"([A-Z]+(?:-[A-Z0-9]+)?)"', src))
    listed = {r["rule"] for r in dashboard.rules()}
    assert raised <= listed, raised - listed
    assert listed - {"SCHEMA", "SCHEMA-000", "REPO-CONFLICT", "SCHEMA-TEXT"} <= raised | {"SCHEMA"}, listed - raised
    for r in dashboard.rules():
        assert r["basis"] in ("sentence", "table", "reference", "inference", "tool")
        if r["basis"] == "sentence":
            assert r["spec"], r["rule"]
        if r["spec"]:
            assert len(r["spec"]["quote"]) >= 25, r["rule"]


def test_repository_governs_and_conflicts_are_information():
    from mpegi_sd_validator.validate import SCHEMA_DISAGREES
    from mpegi_sd_validator.extensions import governs
    assert set(SCHEMA_DISAGREES) == {("MPEG_anchor", "'geoCoordinate' is a required property"),
                                     ("MPEG_viewport_recommended", "'viewports' is a required property")}
    assert governs("MPEG_anchor") == "repository" and governs("MPEG_node_avatar") == "repository"
    assert governs("MPEG_media") == "pdf" and governs("MPEG_viewport_recommended") == "pdf"
    d = good()
    d["extensions"]["MPEG_anchor"]["trackables"] = [{"type": 6, "coordinate": [6.1, 46.2, 400.0]}]
    found = validate_document(d, "x.gltf")
    assert not [f for f in found if f.severity == "error" and f.rule in ("SCHEMA", "ANC-005")]
    assert any(f.rule == "REPO-CONFLICT" and f.severity == "info" for f in found)


def test_viewport_where_the_pdf_governs():
    d = good()
    d["extensions"]["MPEG_viewport_recommended"] = {"name": "one"}
    d["extensionsUsed"].append("MPEG_viewport_recommended")
    found = validate_document(d, "x.gltf")
    assert not [f for f in found if f.severity == "error"]
    assert any(f.rule == "SCHEMA-TEXT" and f.severity == "info" for f in found)


def warn(mutate, rule):
    d = good()
    mutate(d)
    assert (rule, "warning") in rules(d), [f.line() for f in validate_document(d)]


def test_required_extension_not_used():
    case(lambda d: d.update({"extensionsRequired": ["MPEG_texture_video", "MPEG_viewport_recommended"]}), "EXT-004")


def test_start_time_with_autoplay_is_a_warning():
    warn(lambda d: d["extensions"]["MPEG_media"]["media"][0].update({"startTime": 1.0}), "MEDIA-003")


def test_empty_time_range_is_a_warning():
    warn(lambda d: d["extensions"]["MPEG_media"]["media"][0].update({"startTimeOffset": 5, "endTimeOffset": 1}), "MEDIA-004")


def test_track_missing_in_an_alternative():
    def m(d):
        d["extensions"]["MPEG_media"]["media"][0]["alternatives"][0]["tracks"] = [{"track": "#t0"}]
        d["buffers"][0]["extensions"]["MPEG_buffer_circular"]["tracks"] = [3]
    case(m, "BUF-003")


def test_timed_header_buffer_view_missing():
    case(lambda d: d["accessors"][0]["extensions"]["MPEG_accessor_timed"].update({"bufferView": 9}), "ACC-003")


def test_timed_header_in_another_buffer():
    def m(d):
        d["buffers"].append({"byteLength": 8})
        d["bufferViews"].append({"buffer": 1, "byteLength": 8})
        d["accessors"][0]["extensions"]["MPEG_accessor_timed"]["bufferView"] = 1
    case(m, "ACC-004")


def test_texture_accessor_missing():
    case(lambda d: d["textures"][0]["extensions"]["MPEG_texture_video"].update({"accessor": 9}), "TEX-001")


def test_texture_accessor_not_timed():
    case(lambda d: d["accessors"][0]["extensions"].pop("MPEG_accessor_timed"), "TEX-002")


def test_audio_node_needs_source_or_listener():
    def m(d):
        d["extensionsUsed"].append("MPEG_audio_spatial")
        d["nodes"][0]["extensions"]["MPEG_audio_spatial"] = {}
    case(m, "AUD-001")


def test_audio_file_level_needs_reverb():
    def m(d):
        d["extensionsUsed"].append("MPEG_audio_spatial")
        d["extensions"]["MPEG_audio_spatial"] = {}
    case(m, "AUD-002")


def test_anchor_reference_without_definitions():
    case(lambda d: d["extensions"].pop("MPEG_anchor"), "ANC-002")


def test_anchor_trackable_index():
    case(lambda d: d["extensions"]["MPEG_anchor"]["anchors"][0].update({"trackable": 5}), "ANC-004")


def test_marker_node_exists():
    case(lambda d: d["extensions"]["MPEG_anchor"]["trackables"].append({"type": 4, "markerNode": 9}), "ANC-006")


def test_geo_values_in_range():
    def m(d):
        d["extensions"]["MPEG_anchor"]["trackables"].append({"type": 6, "coordinates": [200.0, 100.0, 0.0]})
    d = good(); m(d)
    got = rules(d)
    assert ("ANC-007", "error") in got and ("ANC-008", "error") in got


def interactive(d, **over):
    d["extensionsUsed"].append("MPEG_scene_interactivity")
    ext = {"triggers": [{"type": 0, "nodes": [0]}], "actions": [{"type": 0, "nodes": [0]}], "behaviors": [{"triggers": [0], "actions": [0]}]}
    ext.update(over)
    d["scenes"][0].setdefault("extensions", {})["MPEG_scene_interactivity"] = ext


def test_behavior_refers_to_missing_trigger():
    d = good(); interactive(d, behaviors=[{"triggers": [4], "actions": [0]}])
    assert ("INT-001", "error") in rules(d)


def test_trigger_refers_to_missing_node():
    d = good(); interactive(d, triggers=[{"type": 0, "nodes": [7]}])
    assert ("INT-002", "error") in rules(d)
