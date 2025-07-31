# sensor-fusion-io

SDK for working with sensor fusion scenes

## Installation

```
pip install scale-sensor-fusion-io
```

## Requirements

Minimum Python version supported is:
- 3.10 for >= 0.5.0
- 3.8 for < 0.5.0

# Code samples

## End-to-End Example From PandaSet

[Here](examples/pandas_to_sfs_conversion.ipynb) is a link to a Jupyter notebook example.

## Constructing an SFS scene

### PosePath Dataframe

## Encoding a SFS scene

```
import scale_sensor_fusion_io as sfio
from scale_sensor_fusion_io.model_converters to_scene_spec_sfs
from scale_json_binary import write_file

scene = sfio.Scene() # your scene here
scene_sfs = to_scene_spec_sfs(scene)
import scale_sensor_fusion_io as sfio

write_file(f'~/scene.sfs', scene_sfs)


```

## Loading sfs file

There is a SFSLoader class that provides helper functions for loading a scene from url. There are few variations of loading function, depending on your use case.

```
from scale_sensor_fusion_io.loaders import SFSLoader
scene_url = "~/scene.sfs"

# Not recommended, but possible
raw_scene = SFSLoader(scene_url).load_unsafe() # scene is dict
sfs_scene = SFSLoader(scene_url).load_as_sfs() # scene is SFS.Scene
scene = SceneLoader(scene_url).load() # scene is models.Scene

```

## Validating SFS

Before you upload a scene for task creation, you'll want to validate that your sfs scene is well formed. You can do this in a variety of ways.

### Validating scene object

If you're working with the model.Scene object, you can use the `validate_scene` method available under scale_sensor_fusion_io.models.validation

```
import scale_sensor_fusion_io as sfio
import pprint

scene = sfio.Scene() #

errors = validate_scene(scene)
if errors:
    pp.pprint(asdict(errors))
else:
    print("Scene validated successfully")
```

### Validating from url

If you've already generated a .sfs file, you can also validate that it is well formed

```
from scale_sensor_fusion_io.validation import parse_and_validate_scene
from scale_json_binary import read_file
import pprint

pp = pprint.PrettyPrinter(depth=6)

scene_url = "your_scene.sfs"

raw_data = read_file(scene_url)
result = parse_and_validate_scene(raw_data)

if not result.success:
    pp.pprint(asdict(result))
else:
    print("Scene parsed and validated successfully")
```

# FAQ

## Resulting scene file is too large

For scenes that span a large timeframe, the size of the resulting .sfs file may increase to multi-GBs. This is not ideal for loading onto LidarLite.

### Video encoding

One easy way to reduce scene size is to encode camera content as video, as the video content can be more easily compressed. The tradeoff is the potentially reduced quality of images, but for labeling 3D scenes, this is often sufficient.

See .utils/generate_video.py for helper functions

### Downsample point clouds

Another option is to downsample lidar point clouds. If your scene is used primarily for cuboid annotation, we recommend voxel downsampling using voxel sizes of at most 20mm.

A good heuristic for efficient loading and labeling is to have a scene contain no more than 100,000 points.
