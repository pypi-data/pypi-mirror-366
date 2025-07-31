from dataclasses import dataclass
from typing import Literal, Optional, Sequence, Union

import numpy as np
import numpy.typing as npt

from ...common import SensorID, SensorKind
from ...paths import PosePath


@dataclass
class RadarSensorPoints:
    positions: npt.NDArray[np.float32]
    directions: Optional[npt.NDArray[np.float32]] = None
    lengths: Optional[npt.NDArray[np.float32]] = None
    timestamps: Optional[Union[npt.NDArray[np.uint32], npt.NDArray[np.uint64]]] = None


@dataclass
class RadarSensorFrame:
    timestamp: int
    points: RadarSensorPoints


@dataclass
class RadarSensor:
    id: SensorID
    poses: PosePath
    frames: Sequence[RadarSensorFrame]
    type: Literal[SensorKind.Radar] = SensorKind.Radar
    coordinates: Literal["ego", "world"] = "world"
    parent_id: Optional[SensorID] = None
