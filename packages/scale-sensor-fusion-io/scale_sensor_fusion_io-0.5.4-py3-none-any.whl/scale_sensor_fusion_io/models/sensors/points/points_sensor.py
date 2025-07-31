from dataclasses import dataclass
from typing import List, Literal, Optional, Union, Sequence

import numpy as np
import numpy.typing as npt

from ...common import SensorID, SensorKind
from ...paths import PosePath


# Define PointsSensorPoints dataclass
@dataclass
class Points:
    positions: npt.NDArray[np.float32]
    colors: Optional[npt.NDArray[np.uint8]] = None


# Define PointsSensor dataclass
@dataclass
class PointsSensor:
    id: SensorID
    points: Points
    parent_id: Optional[SensorID] = None
    type: Literal[SensorKind.Points] = SensorKind.Points
