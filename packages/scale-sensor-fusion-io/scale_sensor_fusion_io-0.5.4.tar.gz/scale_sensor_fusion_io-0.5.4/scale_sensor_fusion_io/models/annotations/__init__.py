from typing import Union

from .attributes import *
from .box_2d import *
from .cuboid import *
from .event import *
from .labeled_points import *
from .localization_adjustment import *
from .object import *
from .polygon import *
from .polygon_topdown import *
from .polyline import *

Annotation = Union[
    AttributesAnnotation,
    Box2DAnnotation,
    CuboidAnnotation,
    EventAnnotation,
    LabeledPointsAnnotation,
    LocalizationAdjustmentAnnotation,
    ObjectAnnotation,
    PolygonAnnotation,
    TopdownPolygonAnnotation,
    PolylineAnnotation,
]
