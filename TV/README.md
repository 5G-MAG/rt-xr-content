
## scene

### Summary
a CRT TV set playing a movie


### Extensions used

- MPEG_media
- MPEG_buffer_circular
- MPEG_accessor_timed
- MPEG_audio_spatial
- MPEG_texture_video

### Screeshot
![screenshot](metadata/scene.jpg)

### Legal

&#169; 2016, RDW MIC, Małopolska's Virtual Museums project, <a alt="license" href="https://creativecommons.org/public-domain/cc0/">CC0 Public Domain</a>

  - TV set 3D model (https://skfb.ly/NnEr)

&#169; 2008, Blender Foundation, <a alt="license" href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>

  - Big Buck Bunny movie

&#169; 2023, MotionSpell, <a alt="license" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>

  - added video texture & audio source


## scene_ycbcr

### Summary
`scene` with a planar YCbCr 4:2:0 video texture (`VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM`). The media pipeline stores the decoded Y, Cb and Cr planes as they are, and the renderer converts them to RGB as the `MPEG_sampler_YCbCr` sampler describes: BT.601, narrow range, chroma cosited horizontally and midpoint vertically.


### Extensions used

- MPEG_media
- MPEG_buffer_circular
- MPEG_accessor_timed
- MPEG_audio_spatial
- MPEG_texture_video
- MPEG_sampler_YCbCr

### Screeshot
![screenshot](metadata/scene.jpg)

### Legal

Same as `scene`.
