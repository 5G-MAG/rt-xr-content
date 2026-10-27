## rtxrcontent.py

helper script to push content to device 

### Installation:

create a virutal environment
```
python3 -m venv .venv
```

activate it
```
source venv/bin/activate
```

install dependencies
```
pip install click
```


to use the script, activate the virtual environment.


### Push content directories to default device rt-xr-player directory:
```
./rtxrcontent.py push awards ar-video-plane furnitures studio_apartment
```

### Create and push config file to default device rt-xr-player directory:
```
./rtxrcontent.py config awards ar-video-plane furnitures studio_apartment
```

## mpegsd.py

helper script to add MPEG-I Scene Description interactivity (`MPEG_scene_interactivity`) to a glTF file from the command line.
It reads the glTF file and writes the changed JSON to the standard output.

### Installation:

same virtual environment as `rtxrcontent.py`, with the extra dependencies
```
pip install click json-merge-patch pyjsonpatch
```

### Commands:

```
./mpegsd.py add-trigger-proximity scene.gltf 2.0 -n 3
./mpegsd.py add-trigger-visibility scene.gltf 5.0 -n 3
./mpegsd.py add-action-animation scene.gltf 0 PLAY
./mpegsd.py add-behavior scene.gltf -t 0 -a 0 -x FIRST_ENTER
./mpegsd.py inspect scene.gltf /scenes/0/extensions
./mpegsd.py apply-merge-patch scene.gltf patch.json
./mpegsd.py create-merge-patch scene.gltf modified.gltf
./mpegsd.py apply-patch scene.gltf patch.json
```

`create-patch` is not implemented. `validate` runs a container named `gltfconformance:latest` with `podman`. The commands were not run when this file was documented.
