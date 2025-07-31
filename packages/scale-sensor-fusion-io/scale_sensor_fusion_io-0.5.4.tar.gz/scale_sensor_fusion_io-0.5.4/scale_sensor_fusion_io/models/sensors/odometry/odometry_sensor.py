from dataclasses import dataclass
from typing import Literal, Optional

from ...common import SensorID, SensorKind
from ...paths import PosePath


# Define Odometry dataclass
@dataclass
class OdometrySensor:
    id: SensorID
    poses: PosePath
    parent_id: Optional[SensorID] = None
    type: Literal[SensorKind.Odometer] = SensorKind.Odometer
