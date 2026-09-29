<p align="center">
  <img src=".github/banner.svg" width="100%" alt="Reference Tools · XR/3D Scenes with MPEG-I Scene Description: XR/3D Scenes and Test Content">
</p>

<p align="center">
  Reference glTF scenes for demonstrating and testing the
  <a href="https://github.com/5G-MAG/rt-xr-unity-player">XR Unity Player</a>.
</p>

<p align="center">
  <img alt="Status: Under Development"
    src="https://img.shields.io/badge/Status-Under%20Development-e67e22">
  <a href="https://github.com/5G-MAG/rt-xr-content/releases"><img alt="Version"
    src="https://img.shields.io/github/v/release/5G-MAG/rt-xr-content?label=Version"></a>
  <a href="LICENSE"><img alt="License: multiple, per asset"
    src="https://img.shields.io/badge/License-Multiple%2C%20per%20asset-blue"></a>
</p>

<p align="center">
  <a href="https://www.5g-mag.com/reference-tools/xr/">Project page</a> &nbsp;&middot;&nbsp;
  <a href="https://github.com/5G-MAG/rt-xr-content/issues">Issues</a> &nbsp;&middot;&nbsp;
  <a href="https://www.5g-mag.com/contributing">Contributing</a>
</p>

---

## At a glance

|  |  |
|---|---|
| **Part of** | [XR/3D Scenes with MPEG-I Scene Description](https://www.5g-mag.com/reference-tools/xr/), alongside [rt-xr-unity-player](https://github.com/5G-MAG/rt-xr-unity-player), [rt-xr-gITFast](https://github.com/5G-MAG/rt-xr-gITFast), [rt-xr-maf-native](https://github.com/5G-MAG/rt-xr-maf-native) and [rt-xr-blender-exporter](https://github.com/5G-MAG/rt-xr-blender-exporter) |

## Introduction

This repository holds glTF scenes that use the MPEG-I Scene Description glTF extensions, for
demonstrations and tests with the [XR Unity Player](https://github.com/5G-MAG/rt-xr-unity-player).
Each asset has its own directory with its glTF files and media; most also have a `metadata/`
directory recording ownership, licence and a screenshot. Scenes are pushed to an Android device
as described in the XR Unity Player's README.

More documentation is on the [project page](https://www.5g-mag.com/reference-tools/xr/).

### Available content

More detail on each asset is in its directory.

#### Reference assets for demonstration

##### Studio apartment

<table>
<tr>
<th>Asset</th>
<th>Description</th>
<th>Properties</th>
</tr>
<tr>
<td width="400px">
<a href="studio_apartment"><b>studio_apartment.gltf</b></a><br>
<img src="studio_apartment/metadata/studio_apartment.png" alt="studio_apartment"/>
</td>
<td>
Reference asset to demonstrate <b>MEDIA</b>, in a scene representing a studio apartment
</td>
<td>
<b>MPEG_media</b><br>
<b>MPEG_accessor_timed</b><br>
<b>MPEG_buffer_circular</b><br>
<b>MPEG_texture_video</b><br>
<b>MPEG_audio_spatial</b>
</td>
</tr>
</table>

##### The Academy Award

<table>
<tr>
<th>Asset</th>
<th>Description</th>
<th>Properties</th>
</tr>
<tr>
<td width="400px">
<a href="awards"><b>awards_floor_anchoring.gltf, awards_plane_anchoring.gltf, awards_marker2D.gltf</b></a><br>
<img src="awards/metadata/scene.jpg" alt="scene"/>
</td>
<td>
Reference asset to demonstrate <b>ANCHORING</b>, with a 3D model of the Academy Award statuette
</td>
<td>
<b>MPEG_anchor</b>
</td>
</tr>
</table>

##### Furniture

<table>
<tr>
<th>Asset</th>
<th>Description</th>
<th>Properties</th>
</tr>
<tr>
<td width="400px">
<a href="furnitures"><b>sofa_floor_anchoring.gltf, scene_extra_camera.gltf</b></a><br>
<img src="furnitures/metadata/scene.png" alt="scene"/>
</td>
<td>
Reference asset to demonstrate <b>ANCHORING</b>, with a 3D model of a small sofa
</td>
<td>
<b>MPEG_anchor</b>
</td>
</tr>
</table>

#### Reference assets for testing

The assets for testing are listed in [test_content.md](/test_content.md).

## Downloading

[Git LFS](https://git-lfs.com/) must be installed to clone the repository properly:

```
git lfs install
git clone https://github.com/5G-MAG/rt-xr-content.git
```

## Contributing

Contributions are welcome. How to raise an issue, fork the repository and open a pull request, and
the Contributor License Agreement required before code can be merged, are described at
<https://www.5g-mag.com/contributing>.

Open pull requests against the `development` branch. Every contributed model must meet these rules:

- It passes the glTF-Validator.
- It provides its own metadata and a screenshot.
- Its metadata includes correct and complete legal information (ownership, copyright and licence).
- Its directory has a README. The `gen-readme` command of [rtxrcontent.py](rtxrcontent.py) (set-up in
  [scripts.md](scripts.md)) drafts one from the metadata files; the README can then be extended, for
  example with usage or a longer description.

The metadata file has this JSON format:
```
{
    "version": 2,
    "legal": [
        {
            "owner": "",
            "year": "",
            "license": "",
            "licenseUrl": "",
            "what": ""
        }
    ],
    "tags": [],
    "screenshot": "metadata/screenshot.jpg",
    "name": "",
    "path": "",
    "summary": ""
}
```

- **version**: every metadata file in the repository sets it (2; 1 in `studio_apartment`). `rtxrcontent.py` does not read it, and `gen-metadata` writes it only if the template file passed to it contains it.
- **path**: relative to the glTF file.
- **tags**: curated. The tags in use are "testing" and "demo".

## License

The repository contains content under different licences, listed per folder in [LICENSE](LICENSE):
5G-MAG Public License v1.0 for the `anchoring`, `geometry` and `gravity` scenes
([LICENSE-5G-MAG-PL-1.0](LICENSE-5G-MAG-PL-1.0)), Creative Commons licences for the third-party
scenes, and `ar-video-plane` courtesy of CCMA. Each asset with a `metadata/` directory also records its
ownership, copyright and licence in the `legal` entry of its JSON files; check it before reusing an
asset.
