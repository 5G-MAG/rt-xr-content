## Overview

This directory contains a 3D asset figuring the academy statuette. 

Multiple variants of the gltf documents are provided. These are all based on the base `scene.gltf` document containing the bare model without any MPEG extension.

### Screeshot

![screenshot](metadata/scene.jpg)


### Legal

&#169; 2021, <a alt="sketchfab link" href="https://sketchfab.com/WirtualneMuzeaMalopolski">Virtual Museums of Małopolska</a>, <a alt="license" href="https://creativecommons.org/public-domain/cc0/">CC0 Public Domain</a>


## awards.gltf

A 3D asset figuring the academy statuette, no gltf extension are used in this scene.

### Extensions used

None


## awards_floor_anchoring.gltf

This variant of the base model uses `MPEG_anchor` extension to signal anchoring to the floor in XR applications. 

### Extensions used

- MPEG_anchor

## awards_marker2D.gltf

This variant of the base model uses `MPEG_anchor` extension to signal anchoring to a 2D marker. Here the 5GMAG logo is used as 2D marker : 

<img src="textures/marker.jpg" alt="2D marker" width="200"/>


Instructions: 
- Locate the marker file **awards/textures/marker.jpg**
- Print the marker on a white sheet of paper. Alternatiively, displaying the marker on a screen should also work.
- Launch the scene and point the camera at the marker. The whole marker should be captured for successfull detection. The marker does not need to be horizontal, but it must be exposed a a flat surface.
- Once the marker has been detected, the model will be instantiated and remain anchored to the marker.


### Extensions used

- MPEG_anchor


## awards_plane_anchoring.gltf

This variant of the base model uses `MPEG_anchor` extension to signal anchoring to an hortizontal plane in XR applications. 


### Extensions used

- MPEG_anchor

