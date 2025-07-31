from dataclasses import dataclass
from typing import List, Literal, Optional

from ..common import AnnotationID, AnnotationKind, SensorID
from ..paths import AttributePath

@dataclass
class ObjectAnnotation:
    id: AnnotationID
    type: Literal[AnnotationKind.Object] = AnnotationKind.Object
    parent_id: Optional[AnnotationID] = None
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None

