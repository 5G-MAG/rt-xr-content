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