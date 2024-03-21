
## rt-xr-content

This repository provides test content for the XR Player.

Make sure to visit the [wiki section of the XR Player](https://5g-mag.github.io/Getting-Started/pages/xr-media-integration-in-5g/) for more information on the project.


## Questions or Comments

If you have any questions, please submit an issue.


## Listing

See individual directory for detailed informations.

<table>
<tr>
<th>Model</th>
<th>Description</th>
</tr>
<tr>
<td>
<a href="interactivity">UseCase_01-variant3-Interactivity</a><br/>
<img src="interactivity/metadata/UseCase_01-variant3-Interactivity.jpg" alt="UseCase_01-variant3-Interactivity"/>
</td>
<td>
demonstrates interactivity using TRIGGER_COLLISION to activate ACTION_SET_MATERIAL and ACTION_MEDIA<br/>
<tr>
<td>
<a href="interactivity">UseCase_02-variant3-Interactivity</a><br/>
<img src="interactivity/metadata/UseCase_02-variant3-Interactivity.jpg" alt="UseCase_02-variant3-Interactivity"/>
</td>
<td>
demonstrates interactivity behavior using TRIGGER_VISIBILTIY to activate ACTION_MEDIA<br/>
<tr>
<td>
<a href="interactivity">UseCase_03-variant1-Interactivity</a><br/>
<img src="interactivity/metadata/UseCase_03-variant1-Interactivity.jpg" alt="UseCase_03-variant1-Interactivity"/>
</td>
<td>
demonstrates interactivity using TRIGGER_PROXIMITY to activate ACTION_ANIMATION and ACTION_MEDIA<br/>
<tr>
<td>
<a href="interactivity">UseCase_03-variant3-Interactivity</a><br/>
<img src="interactivity/metadata/UseCase_03-variant3-Interactivity.jpg" alt="UseCase_03-variant3-Interactivity"/>
</td>
<td>
demonstrates interactivity using TRIGGER_USER_INPUT to activate ACTION_ANIMATION<br/>
<tr>
<td>
<a href="TV">scene</a><br/>
<img src="TV/metadata/scene.jpg" alt="scene"/>
</td>
<td>
a CRT TV set playing a movie<br/>
<tr>
<td>
<a href="video">scene-av-combined</a><br/>
<img src="video/metadata/scene.jpg" alt="scene-av-combined"/>
</td>
<td>
audio and video packaged as seperate tracks of a single mp4, explicit track to buffer mapping<br/>
<tr>
<td>
<a href="video">scene-av-independant</a><br/>
<img src="video/metadata/scene.jpg" alt="scene-av-independant"/>
</td>
<td>
audio and video packaged in separate mp4 files<br/>
<tr>
<td>
<a href="video">scene</a><br/>
<img src="video/metadata/scene.jpg" alt="scene"/>
</td>
<td>
a living room scene demonstrating video texture<br/>
</table>


## Contributing 

In order to contribute, open a pull request on the `development` branch.

For all contributions, the following items are expected:


All submitted models must pass the glTF-Validator.

Each model must provide its own metadata and be illustrated with a screenshot. 

The metadata must include the correct and complete legal information (ownership, copyright, and license).

A README for the subdirectory containing the model. A script is proposed to generate these README draft from the metadata files. The README files submitted can be extended with additionnal information (eg. usage, extended description, ...).

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
- **tags** : tags will be currated. Currently, "testing" is the only tag used. 
