from dataclasses import dataclass
from typing import List, Literal, Optional

from ..common import AnnotationID, AnnotationKind, SensorID
from ..paths import AttributePath, CuboidPath


@dataclass
class CuboidActivationPath:
    sensor_id: SensorID
    timestamps: List[int]
    durations: List[float]
    cuboids: Optional[List[List[float]]]  # x y z yaw pitch roll dx dy dz


@dataclass
class CuboidProjectionPath:
    sensor_id: SensorID  # 2d sensor like cameras
    timestamps: List[int]
    boxes: List[
        Optional[List[float]]
    ]  # x y width height; Can be None if cuboid can't be projected or if projection is actively deleted
    cuboids: Optional[List[List[float]]]  # dx dy dz px py pz roll pitch yaw


@dataclass
class CuboidAnnotation:
    id: AnnotationID
    path: CuboidPath
    label: Optional[str] = None
    stationary: Optional[bool] = False
    type: Literal[AnnotationKind.Cuboid] = AnnotationKind.Cuboid
    attributes: Optional[List[AttributePath]] = None
    activations: Optional[List[CuboidActivationPath]] = None
    projections: Optional[List[CuboidProjectionPath]] = None
    parent_id: Optional[AnnotationID] = None
