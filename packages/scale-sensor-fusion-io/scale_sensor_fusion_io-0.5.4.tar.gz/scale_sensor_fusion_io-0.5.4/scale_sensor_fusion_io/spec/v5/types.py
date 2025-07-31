from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

import scale_sensor_fusion_io.spec.sfs as SFS

SensorID = SFS.SensorID
AnnotationID = SFS.AnnotationID

PosePath = SFS.PosePath

PointsSensorPoints = SFS.PointsSensorPoints
PointsSensor = SFS.PointsSensor

LidarSensorPoints = SFS.LidarSensorPoints
LidarSensorFrame = SFS.LidarSensorFrame
LidarSensor = SFS.LidarSensor

RadarSensorPoints = SFS.RadarSensorPoints
RadarSensorFrame = SFS.RadarSensorFrame
RadarSensor = SFS.RadarSensor

DistortionModel = SFS.DistortionModel
CameraDistortion = SFS.CameraDistortion

CameraIntrinsics = SFS.CameraIntrinsics

CameraSensorVideo = SFS.CameraSensorVideo
CameraSensorImage = SFS.CameraSensorImage
CameraSensor = SFS.CameraSensor

OdometrySensor = SFS.OdometrySensor

AttributePath = SFS.AttributePath

CuboidPath = SFS.CuboidPath
CuboidActivationPath = SFS.CuboidActivationPath
CuboidProjectionPath = SFS.CuboidProjectionPath


@dataclass
class StaticPath:
    timestamps: List[int]
    values: List[bool]


@dataclass
class CuboidMetadata:
    static_path: Optional[StaticPath] = None


@dataclass
class _CuboidAnnotationBase:
    cuboid_metadata: CuboidMetadata


@dataclass
class CuboidAnnotation(SFS.CuboidAnnotation, _CuboidAnnotationBase):
    pass


AttributesAnnotation = SFS.AttributesAnnotation
AnnotationPath = SFS.AnnotationPath
Box2DAnnotation = SFS.Box2DAnnotation
Polygon2DAnnotation = SFS.Polygon2DAnnotation
Point2DAnnotation = SFS.Point2DAnnotation
PointAnnotation = SFS.PointAnnotation
PolylineAnnotation = SFS.PolylineAnnotation
PolygonAnnotation = SFS.PolygonAnnotation
TopdownPolygonAnnotation = SFS.TopdownPolygonAnnotation
TopdownPointAnnotation = SFS.TopdownPointAnnotation
Polyline2DAnnotation = SFS.Polyline2DAnnotation
EventAnnotation = SFS.EventAnnotation
LabeledPoint = SFS.LabeledPoint
LabeledPointsAnnotation = SFS.LabeledPointsAnnotation


@dataclass
class LinkMetadata:
    anchored: Optional[bool] = False


## NOTE: This is implemented this way to be able to inherit from the SFS dataclasses, which contain defaults
@dataclass
class _LinkAnnotationBase:
    metadata: LinkMetadata


@dataclass
class LinkAnnotation(SFS.LinkAnnotation, _LinkAnnotationBase):
    pass


class CuboidLayerMode(Enum):
    Position = "position"
    PositionRotation = "position-rotation"
    ZLevel = "z-level"
    XY = "XY"
    ICP = "icp"


@dataclass
class LocalizationAdjustmentLayerMetadata:
    layer_type: Literal["base", "cuboid"]
    order: int
    name: str
    cuboids: Optional[List[CuboidPath]] = None
    algorithm: Optional[CuboidLayerMode] = None


## NOTE: This is implemented this way to be able to inherit from the SFS dataclasses, which contain defaults
@dataclass
class _LocalizationAdjustmentAnnotationBase:
    layer_metadata: LocalizationAdjustmentLayerMetadata


@dataclass
class LocalizationAdjustmentAnnotation(
    SFS.LocalizationAdjustmentAnnotation, _LocalizationAdjustmentAnnotationBase
):
    pass


ObjectAnnotation = SFS.ObjectAnnotation

Sensor = Union[CameraSensor, LidarSensor, RadarSensor, OdometrySensor, PointsSensor]


Annotation = Union[
    CuboidAnnotation,
    AttributesAnnotation,
    Box2DAnnotation,
    Point2DAnnotation,
    Polyline2DAnnotation,
    Polygon2DAnnotation,
    TopdownPolygonAnnotation,
    TopdownPointAnnotation,
    PolygonAnnotation,
    PolylineAnnotation,
    PointAnnotation,
    LinkAnnotation,
    LabeledPointsAnnotation,
    LocalizationAdjustmentAnnotation,
    ObjectAnnotation,
]


@dataclass
class Scene:
    version: Literal["5.1", "1.0"] = "5.1"
    sensors: Optional[List[Sensor]] = None
    annotations: Optional[List[Annotation]] = None
    attributes: Optional[List[AttributePath]] = None
    time_offset: Optional[int] = None
    time_unit: Optional[Literal["microseconds", "nanoseconds"]] = "microseconds"
    metadata: Optional[Dict[str, Any]] = None
