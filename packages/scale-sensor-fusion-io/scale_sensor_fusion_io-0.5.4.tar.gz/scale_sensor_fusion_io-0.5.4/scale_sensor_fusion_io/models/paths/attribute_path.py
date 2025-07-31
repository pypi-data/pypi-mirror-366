from dataclasses import dataclass
from typing import List, Optional, Union

from ..common import SensorID


@dataclass
class AttributePath:
    name: str
    timestamps: List[int]
    values: List[Union[str, int, List[str]]]
    sensor_id: Optional[SensorID] = None
    static: bool = False
