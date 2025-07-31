from dataclasses import dataclass
from typing import List, Literal, Optional

from scale_sensor_fusion_io.models.paths.cuboid_path import CuboidPath

from ..common import AnnotationID, AnnotationKind
from ..paths import PosePath
"""
The LocalizationAdjustmentAnnotation represents a PosePath applied a scene to fix localization issues or convert from ego to world coordinates.
"""


@dataclass
class LayerMetadata:
    layer_type: Literal["base", "cuboid"]
    order: int
    name: str
    cuboids: Optional[List[CuboidPath]] = None
    algorithm: Optional[
        Literal["position", "position-rotation", "z-level", "icp"]
    ] = None

@dataclass
class LocalizationAdjustmentAnnotation:
    id: AnnotationID
    poses: PosePath
    type: Literal[AnnotationKind.LocalizationAdjustment] = AnnotationKind.LocalizationAdjustment
    parent_id: Optional[AnnotationID] = None
    layer_metadata: Optional[LayerMetadata] = None
