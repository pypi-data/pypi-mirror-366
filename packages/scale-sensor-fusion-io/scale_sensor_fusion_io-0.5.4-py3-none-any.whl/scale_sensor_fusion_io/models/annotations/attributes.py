from dataclasses import dataclass
from typing import List, Union, Optional, Literal

from ..common import AnnotationID, AnnotationKind, SensorID
from ..paths import AttributePath

# Define AttributesAnnotation dataclass
@dataclass
class AttributesAnnotation:
    id: AnnotationID
    type: Literal[AnnotationKind.Attributes] = AnnotationKind.Attributes
    parent_id: Optional[AnnotationID] = None
    attributes: Optional[List[AttributePath]] = None

