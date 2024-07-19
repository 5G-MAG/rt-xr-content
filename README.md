<h1 align="center">Content for the XR Unity Player</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Status-Under_Development-yellow" alt="Under Development">
  <img src="https://img.shields.io/github/v/tag/5G-MAG/rt-xr-content?label=version" alt="Version">
</p>

# Introduction
This repository provides reference content for testng and demos with the XR Player.

Additional information can be found at: https://5g-mag.github.io/Getting-Started/pages/xr-media-integration-in-5g/

# Available content

See individual directories for detailed information.

## Reference assets for demonstration

### Studio apartment

<table>
<tr>
<th>Asset</th>
<th>Description</th>
<th>Properties</th>
</tr>

<tr>
<td width="400px">
<a href="studio_apartment"><b>studio_apartment.gltf</a></b><br>
<img src="studio_apartment/metadata/studio_apartment.png"  alt="studio_apartment"/>
</td>
<td>
Reference asset to demo <b>MEDIA</b> in a scene represeting a studio apartment<br>
</td>
<td>
<b>MPEG_media</b><br>
<b>MPEG_accessor_timed</b><br>
<b>MPEG_buffer_circular</b><br>
<b>MPEG_texture_video</b><br>
<b>MPEG_audio_spatial</b><br>
<tr>

</table>

### The Academy Award

<table>
<tr>
<th>Asset</th>
<th>Description</th>
<th>Properties</th>
</tr>

<tr>
<td width="400px">
<a href="awards"><b>scene_anchoring.gltf</a></b><br>
<img src="awards/metadata/scene.jpg"  alt="scene"/>
</td>
<td>
Reference asset to demo <b>ANCHORING</b> with a 3D model of the Academy Award statuette<br>
</td>
<td>
<b>MPEG_anchor</b><br>
<tr>
  
</table>

### Furnitures

<table>
<tr>
<th>Asset</th>
<th>Description</th>
<th>Properties</th>
</tr>

<tr>
<td width="400px">
<a href="furnitures"><b>scene.gltf</a></b><br>
<img src="furnitures/metadata/scene.png"  alt="scene"/>
</td>
<td>
Reference asset to demo <b>ANCHORING</b> with a 3D model of a small sofa<br>
</td>
<td>
<b>MPEG_anchor</b><br>
<tr>
  
</table>

## Reference assets for testing

Reference assets for testing are listed [here](/test_content.md).

# Contributing 

In order to contribute, open a pull request on the `development` branch.

For all contributions, the following rules apply:

- All submitted models must pass the glTF-Validator.

- Each model must provide its own metadata and be illustrated with a screenshot. 

- The metadata must include the correct and complete legal information (ownership, copyright, and license).

- A README for the subdirectory containing the model must be created. A script is proposed to generate these README draft from the metadata files. The README files submitted can be extended with additionnal information (eg. usage, extended description, ...).

The metadata file json format is as follow:
```
{
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

- **path** : is relative to the gltf file.
- **tags** : tags will be curated. Currently, "testing" is the only tag used. 

# Questions or Comments

If you have any questions, please submit an issue.
