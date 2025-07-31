from dataclasses import dataclass
from typing import List, Literal, Optional, Union

import numpy as np
import numpy.typing as npt

from ..common import AnnotationID, AnnotationKind, SensorID


# Define LabeledPointsAnnotationLabeledPoint dataclass
@dataclass
class LabeledPoint:
    sensor_id: SensorID
    point_ids: npt.NDArray[np.uint32]
    sensor_frame: Optional[int] = None


# Define LabeledPointsAnnotation dataclass
@dataclass
class LabeledPointsAnnotation:
    id: AnnotationID
    label: str
    labeled_points: List[LabeledPoint]
    is_instance: bool = False
    type: Union[Literal[AnnotationKind.LabeledPoints],Literal[AnnotationKind.PointSegmentation]] = AnnotationKind.PointSegmentation
    parent_id: Optional[AnnotationID] = None
