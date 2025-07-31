from typing import Union

from .points import *
from .camera import *
from .lidar import *
from .radar import *
from .odometry import *

Sensor = Union[
    PointsSensor,
    CameraSensor,
    LidarSensor,
    RadarSensor,
    OdometrySensor,
]
