from dataclasses import dataclass
from typing import List, Literal, Optional

from ..common import AnnotationID, AnnotationKind, SensorID
from ..paths import AttributePath


@dataclass
class PolygonPath:
    timestamps: List[int]
    values: List[List[float]]  # x_0, y_0, x_1, y_1, ..., x_n, y_n


@dataclass
class PolygonAnnotation:
    id: AnnotationID
    sensor_id: SensorID
    path: PolygonPath
    type: Literal[AnnotationKind.Polygon] = AnnotationKind.Polygon
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = False
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None
