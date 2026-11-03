
## scene-av-combined

### Summary
audio and video packaged as seperate tracks of a single mp4, explicit track to buffer mapping


### Extensions used

- MPEG_media
- MPEG_buffer_circular
- MPEG_accessor_timed
- MPEG_audio_spatial
- MPEG_texture_video

### Screeshot
![screenshot](metadata/scene.jpg)

### Legal

&#169; 2019, Carlos Miguel Vieira Maciel, <a alt="license" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>

  - Living Room 3D model (https://skfb.ly/6TAqI)

&#169; 2008, Blender Foundation, <a alt="license" href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>

  - Big Buck Bunny movie

&#169; 2023, MotionSpell, <a alt="license" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>

  - added video texture & audio source to the living room scene


## scene-av-independant

### Summary
audio and video packaged in separate mp4 files


### Extensions used

- MPEG_media
- MPEG_buffer_circular
- MPEG_accessor_timed
- MPEG_audio_spatial
- MPEG_texture_video

### Screeshot
![screenshot](metadata/scene.jpg)

### Legal

&#169; 2019, Carlos Miguel Vieira Maciel, <a alt="license" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>

  - Living Room 3D model (https://skfb.ly/6TAqI)

&#169; 2008, Blender Foundation, <a alt="license" href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>

  - Big Buck Bunny movie

&#169; 2023, MotionSpell, <a alt="license" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>

  - added video texture & audio source to the living room scene


## scene

### Summary
a living room scene demonstrating video texture


### Extensions used

- MPEG_media
- MPEG_buffer_circular
- MPEG_accessor_timed
- MPEG_texture_video

### Screeshot
![screenshot](metadata/scene.jpg)

### Legal

&#169; 2019, Carlos Miguel Vieira Maciel, <a alt="license" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>

  - Living Room 3D model (https://skfb.ly/6TAqI)

&#169; 2008, Blender Foundation, <a alt="license" href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>

  - Big Buck Bunny movie

&#169; 2023, MotionSpell, <a alt="license" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>

  - added video texture & audio source


## scene-video-header

### Summary
`scene` with a timed accessor information header on the video buffer. The header of the RGB accessor is 30 bytes, and the picture starts right after it, at byte 30 of the buffer frame.


### Extensions used

- MPEG_media
- MPEG_buffer_circular
- MPEG_accessor_timed
- MPEG_texture_video

### Screeshot
![screenshot](metadata/scene.jpg)

### Legal

Same as `scene`.


## scene-video-header-aligned

### Summary
`scene-video-header` with the picture at byte 32 of the buffer frame, the next 4-byte boundary after the 30-byte header. This is the layout `gltf-mpeg-media add --video-header` writes.

rt-xr-maf-native 44d697d writes the picture right after the header (byte 30), not at the offset of the bufferView, so the player reads it 2 bytes off: the colours are wrong.


### Extensions used

- MPEG_media
- MPEG_buffer_circular
- MPEG_accessor_timed
- MPEG_texture_video

### Screeshot
![screenshot](metadata/scene.jpg)

### Legal

Same as `scene`.


## scene-av-audio-no-header

### Summary
`scene-av-independant` without a timed accessor information header on the audio buffer. A buffer frame holds exactly the 1024 samples of the accessor.


### Extensions used

- MPEG_media
- MPEG_buffer_circular
- MPEG_accessor_timed
- MPEG_audio_spatial
- MPEG_texture_video

### Screeshot
![screenshot](metadata/scene.jpg)

### Legal

Same as `scene-av-independant`.
