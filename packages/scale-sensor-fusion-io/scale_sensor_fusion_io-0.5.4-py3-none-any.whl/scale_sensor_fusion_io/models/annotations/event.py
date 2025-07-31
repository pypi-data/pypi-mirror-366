from dataclasses import dataclass
from typing import List, Literal, Optional, Union

from ..common import AnnotationID, AnnotationKind, SensorID
from ..paths import AttributePath


@dataclass
class EventAnnotation:
    id: AnnotationID
    start: int
    type: Literal[AnnotationKind.Event] = AnnotationKind.Event
    parent_id: Optional[AnnotationID] = None
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None
    duration: Optional[int] = None
    sensor_id: Optional[SensorID] = None
