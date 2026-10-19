<h1 align="center">MPEG-I Scene Description - XR/3D Scene Validator</h1>

<p align="center">
  Checks glTF files that use the MPEG-I Scene Description extensions against ISO/IEC 23090-14, from the
  command line or on a local web page.
</p>

<p align="center">
  <img alt="Status: under development"
    src="https://img.shields.io/badge/Status-Under%20Development-f39c12">
  <a href="LICENSE"><img alt="License: 5G-MAG Public License v1.0"
    src="https://img.shields.io/badge/License-5G--MAG%20PL%20v1.0-blue"></a>
</p>

---

## At a glance

|  |  |
|---|---|
| **Checks** | `.gltf` and `.glb` files; a folder is searched for them; the scenes of [rt-xr-content](https://github.com/5G-MAG/rt-xr-content) are the reference set |
| **Specification** | ISO/IEC 23090-14; the MPEG repository governs the extensions it changed after the PDF; the PDF governs the others |
| **Schemas** | a dependency, not a copy: the JSON schemas of the MPEG repository (`MPEGGroup/Scene-Description`), pinned to commit 5e39101 and fetched on first use (see Dependencies) |
| **Result** | per scene: each finding with its rule, clause and JSON pointer, as text, JSON, a page and a Markdown report |
| **Runs on** | Linux, Python 3.9 or later, `jsonschema`, `git` (to fetch the MPEG schemas once, or to clone a git URL given on the page) |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .   # the MPEG schemas are fetched on first run, see Dependencies
mpegi-sd-validate scenes/                 # a folder is searched for .gltf and .glb files
mpegi-sd-validate scene.gltf --format json
mpegi-sd-validate scenes/ --summary       # one line per file
```

The exit code is 1 when any file has an error. Every finding names a rule, the clause of the specification it rests on, the
JSON pointer of the object concerned, and what is wrong. Where the specification states no clause for a check, the clause field
is empty or names the glTF 2.0 section.

## Dashboard

```
mpegi-sd-validate --serve <folder> [--port 8092]
```

Opens a page on http://127.0.0.1:8092/ that validates a folder, or a git URL at a branch, tag or commit, with the MPEG schemas of the default (see Dependencies) or of a folder or git repository entered in the second field, lists every scene
with its MPEG extensions and error and warning counts, shows each finding with its rule, clause and JSON pointer, lists
every rule, and exports the result as Markdown or JSON. It uses the same checks as the command line.

## What is checked

1. **The JSON schemas** of the extensions, read from the MPEG repository (see Dependencies).
2. **The rules the schemas cannot express**, written from the requirements of the specification:

| Rule | Clause | What it checks |
|---|---|---|
| EXT-001, EXT-004 | 5.1.1 | every extension used is in `extensionsUsed`, every required one is too |
| EXT-002 | 5.1.1 | an `MPEG_*` name that this document does not define (warning), with the name the text uses (for example `MPEG_node_avatar`) |
| EXT-003 | by extension | an extension sits only where its clause allows (`MPEG_media` at the top level, `MPEG_buffer_circular` on a buffer, `MPEG_viewport_recommended` on a scene, ...) |
| MEDIA-001, 002 | 5.2.1.2 | `autoplayGroup` is an integer and only with `autoplay` true |
| MEDIA-003, 004 | 5.2.1.2 | `startTime` with `autoplay` true (warning); `endTimeOffset` not after `startTimeOffset` (warning) |
| BUF-001 to 004 | 5.2.3 | no `uri`; `media` and `tracks` exist; `byteLength` holds `count` frames (warning) |
| ACC-002 to 006 | 5.2.2 | without a header `immutable` is true; the header bufferView is in the same buffer; a timed accessor is on a circular buffer; a buffer does not mix accessors with and without header |
| TEX-001 to 003 | 5.3.1 | the accessor exists and is timed; the format has as many components as the accessor type |
| AUD-001 to 005 | 5.4.1 | a node has sources or a listener; the file level has a reverb; `reverbFeedGain` and `reverbFeed` have the same length; `clusterProperties` with `isCluster`; no `referenceDistance` for HOA |
| ANC-001 to 008 | 8.1 | anchors defined at file level; not at scene and node level together; anchor and trackable indices; required properties per trackable type; geographic coordinates longitude first, in range |
| INT-001 to 003 | 8.2.2.1 | behavior triggers and actions exist; node indices exist; `userInputDescription` is an OpenXR path name string (clause 6.2 of OpenXR 1.0) |
| VIEW-001 to 003, ANIM-001, MESH-001 to 004 | 5.5.1.2, 5.5.2.2, 5.3.2.2 | the componentType and type of the accessors these extensions reference; the shadow mesh exists |
| GLTF-001, 002 | glTF 2.0 3.6.1.1, 3.6.2.4 | a buffer file is at least `byteLength` long; each accessor fits its bufferView |

## Where the rules come from

`src/mpegi_sd_validator/rules.json` lists every rule with the clause of ISO/IEC 23090-14 it follows, a description in this tool's own
words, and its basis: a requirement of the clause's text, a table of the clause, a reference between indices, or the tool itself. The
Rules tab shows it.

Copyright: no text of ISO/IEC 23090-14 or of the files of the MPEG repository is stored here, only clause numbers and descriptions
written for this tool. The specification is under ISO copyright, and the README files of the MPEG repository carry rights that no
license of that repository grants.

## Which source governs

**Rule.** The more recent source governs, per extension.

| Governs | Extensions (last change to the files in the MPEG repository) |
|---|---|
| the MPEG repository | `MPEG_anchor`, `MPEG_scene_interactivity`, `MPEG_node_interactivity`, `MPEG_haptic`, `MPEG_lights_*` (Nov 2024), `MPEG_haptic_material` (Nov 2024), `MPEG_node_avatar` (May 2025) |
| the PDF | `MPEG_media`, `MPEG_accessor_timed`, `MPEG_buffer_circular`, `MPEG_scene_dynamic`, `MPEG_texture_video`, `MPEG_mesh_linking`, `MPEG_audio_spatial`, `MPEG_viewport_recommended`, `MPEG_animation_timing` (Feb to Mar 2023) |

The table is `extensions.py` (`governs`), from the repository at commit 5e39101.

The repository's JSON schemas check each extension object's structure. Where the repository contradicts itself, for example a
README against a schema file, neither is chosen: the finding is `REPO-CONFLICT` information. Where the PDF governs and a schema
file differs from it, the finding is `SCHEMA-TEXT` information. Known cases:

- trackable of type `TRACKABLE_MARKER_GEO` (repository governs): the README of `MPEG_anchor` names the property `coordinates`; the
  schema file lists `coordinate` and requires `geoCoordinate`. `REPO-CONFLICT`; a scene using either spelling gets the
  information line, not an error;
- `MPEG_viewport_recommended` (PDF governs): Table 19 defines the extension object as one viewport; the schema requires a `viewports`
  array. `SCHEMA-TEXT`;
- `MPEG_media`: a requirement stated only by the README of the extension (from 2023) is not a rule, because the PDF governs;
- the interactivity schemas refer to each other as `MPEG_scene_interactivity.*` while the files are named `MPEG_interactivity.*`:
  the tool resolves both names;
- `MPEG_lights_texture_based.schema.json` is not valid JSON in the repository and is left out (`SCHEMA-000`).

Every rule rests on a requirement or a table of the text, an index reference, or the tool itself (`basis` in `rules.json`). Two
candidate rules were left out because no sentence states them: an accessor on a circular buffer needing `MPEG_accessor_timed` (the text
states the converse, `ACC-005`) and width x height equalling the accessor count.

## What is not checked

- The base glTF 2.0 beyond the two integrity rules above: use the Khronos glTF Validator for it.
- The media itself: whether a declared picture size matches the stream, the codec, or whether a URL answers.
- The `#` index of `triggersCombinationControl` (the text gives an example starting at `#1` and does not say what the number counts).
- Placement of lights and haptics: their schemas are applied wherever they are found.
- The carriage formats of clause 7 (ISO base media file boxes).

## Tests

    pip install -e ".[test]" && pytest   # needs the MPEG schemas: MPEGI_SD_SCHEMAS, or the pinned commit is fetched

`tests/test_rules.py` builds a small valid scene, breaks it in one way per test, and expects the rule (50 tests, every rule above
except `SCHEMA` and `SCHEMA-000` has one).

## Dependencies

This tool contains no file of the MPEG repository. The JSON schemas of the extensions are read at run time from a clone of
https://github.com/MPEGGroup/Scene-Description, found in this order:

1. the repository chosen by the user: the field "MPEG schemas: folder or git repository" of the page (a folder, or a git URL with a
   branch, tag or commit), `--mpeg-schemas DIR_OR_URL` with `--mpeg-schemas-ref REF` on the command line, or the environment variable
   `MPEGI_SD_SCHEMAS` (a folder). A git URL is cloned into the cache folder at that ref. Any clone or commit may be used; a commit other
   than the pinned one is reported, and the table of which source governs each extension (below) was made for the pinned commit;
2. the cache folder (`$XDG_CACHE_HOME` or `~/.cache`, `mpegi-sd-validator/Scene-Description-5e39101`): on first use the tool clones
   the repository there and checks out the pinned commit, `5e39101aa38333248861c62404d992e10ac1f964`. Set `MPEGI_SD_NO_FETCH=1` to
   forbid that; the tool then stops with exit code 2 and says what to do.

Every report names the repository and the commit the schemas came from. The schemas keep the license of the MPEG repository. The few
glTF base schemas those schemas refer to (`schemas/gltf`) are minimal definitions of this tool, not a copy of the Khronos files.

## License

5G-MAG Public License (v1.0), see [LICENSE](LICENSE).
