from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from typing_extensions import Literal

from .annotations import Annotation
from .annotations.attributes import AttributePath
from .sensors import Sensor


@dataclass
class Scene:
    sensors: Optional[List[Sensor]] = None
    annotations: Optional[List[Annotation]] = None
    attributes: Optional[List[AttributePath]] = None
    time_offset: Optional[int] = None
    time_unit: Optional[
        Literal["microseconds", "nanoseconds"]
    ] = "microseconds"
    metadata: Optional[Dict[str, Any]] = None

    def add_sensor(self) -> None:
        pass

