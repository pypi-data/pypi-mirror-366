from dataclasses import dataclass
from typing import List, Literal, Optional, Union, Sequence

import numpy as np
import numpy.typing as npt

from ...common import SensorID, SensorKind
from ...paths import PosePath


# Define LidarSensorPoints dataclass
@dataclass
class LidarSensorPoints:
    positions: npt.NDArray[np.float32]
    colors: Optional[npt.NDArray[np.uint8]] = None
    intensities: Optional[npt.NDArray[np.uint8]] = None
    timestamps: Optional[Union[npt.NDArray[np.uint32], npt.NDArray[np.uint64]]] = None


# Define LidarSensorFrame dataclass
@dataclass
class LidarSensorFrame:
    timestamp: int
    points: LidarSensorPoints


# Define LidarSensor dataclass
@dataclass
class LidarSensor:
    id: SensorID
    poses: PosePath
    frames: Sequence[LidarSensorFrame]
    parent_id: Optional[SensorID] = None
    coordinates: Literal["ego", "world"] = "world"
    type: Literal[SensorKind.Lidar] = SensorKind.Lidar
