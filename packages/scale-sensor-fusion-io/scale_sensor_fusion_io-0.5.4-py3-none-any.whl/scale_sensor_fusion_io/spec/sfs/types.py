from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Union

import numpy as np
import numpy.typing as npt

SensorID = Union[str, int]
AnnotationID = Union[str, int]


# Define PosePath dataclass
@dataclass
class PosePath:
    timestamps: List[int]
    values: List[List[float]]  # x y z qx qy qz qw


# Define PointsSensorPoints dataclass
@dataclass
class PointsSensorPoints:
    positions: npt.NDArray[np.float32]
    colors: Optional[npt.NDArray[np.uint8]]


# Define PointsSensor dataclass
@dataclass
class PointsSensor:
    id: SensorID
    points: PointsSensorPoints
    type: Literal["points"] = "points"
    parent_id: Optional[SensorID] = None


# Define LidarSensorPoints dataclass
@dataclass
class LidarSensorPoints:
    positions: npt.NDArray[np.float32]
    colors: Optional[npt.NDArray[np.uint8]] = None
    intensities: Optional[npt.NDArray[np.uint8]] = None
    timestamps: Optional[Union[npt.NDArray[np.uint32], npt.NDArray[np.uint64]]] = None


# Define LidarSensorFrame dataclass
@dataclass
class LidarSensorFrame:
    timestamp: int
    points: LidarSensorPoints


# Define LidarSensor dataclass
@dataclass
class LidarSensor:
    id: SensorID
    poses: PosePath
    frames: List[LidarSensorFrame]
    parent_id: Optional[SensorID] = None
    coordinates: Literal["ego", "world"] = "world"
    type: Literal["lidar"] = "lidar"


# Define RadarSensorPoints dataclass
@dataclass
class RadarSensorPoints:
    positions: npt.NDArray[np.float32]
    directions: Optional[npt.NDArray[np.float32]] = None
    lengths: Optional[npt.NDArray[np.float32]] = None
    timestamps: Optional[Union[npt.NDArray[np.uint32], npt.NDArray[np.uint64]]] = None


# Define RadarSensorFrame dataclass
@dataclass
class RadarSensorFrame:
    timestamp: int
    points: RadarSensorPoints


# Define RadarSensor dataclass
@dataclass
class RadarSensor:
    id: SensorID
    poses: PosePath
    frames: List[RadarSensorFrame]
    type: Literal["radar"] = "radar"
    coordinates: Literal["ego", "world"] = "world"
    parent_id: Optional[SensorID] = None


# Define DistortionModel enum
DistortionModel = Literal[
    "brown_conrady",
    "mod_equi_fish",
    "mod_kannala",
    "fisheye",
    "fisheye_rad_tan_prism",
    "cylindrical",
    "equirectangular",
    "omnidirectional",
    "fisheye_radial_custom",
    "ftheta",
]


# Define CameraDistortion dataclass
@dataclass
class CameraDistortion:
    model: DistortionModel
    params: List[float]


# Define CameraIntrinsics dataclass
@dataclass
class CameraIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    width: int
    height: int
    distortion: Optional[CameraDistortion]


# Define CameraSensorContent dataclass
@dataclass
class CameraSensorVideo:
    timestamps: List[int]
    content: npt.NDArray[np.uint8]
    fps: float


# Define CameraSensorImages dataclass
@dataclass
class CameraSensorImage:
    timestamp: int
    content: npt.NDArray[np.uint8]


# Define CameraSensor dataclass
@dataclass
class CameraSensor:
    id: SensorID
    poses: PosePath
    intrinsics: CameraIntrinsics
    video: Optional[CameraSensorVideo] = None
    images: Optional[List[CameraSensorImage]] = None
    type: Literal["camera"] = "camera"
    parent_id: Optional[SensorID] = None


# Define OdometrySensor dataclass
@dataclass
class OdometrySensor:
    id: SensorID
    poses: PosePath
    type: Literal["odometry"] = "odometry"
    parent_id: Optional[SensorID] = None


# Define AttributePath dataclass
@dataclass
class AttributePath:
    name: str
    timestamps: List[int]
    values: List[Union[str, int, List[str]]]
    sensor_id: Optional[SensorID] = None
    static: bool = False


# Define CuboidPath dataclass
@dataclass
class CuboidPath:
    timestamps: List[int]
    values: List[List[float]]  # dx dy dz px py pz roll pitch yaw


# Define CuboidActivationPath dataclass
@dataclass
class CuboidActivationPath:
    sensor_id: SensorID
    timestamps: List[int]
    durations: List[float]
    cuboids: Optional[List[List[float]]]  # dx dy dz px py pz roll pitch yaw


# Define CuboidProjectionPath dataclass
@dataclass
class CuboidProjectionPath:
    sensor_id: SensorID  # 2d sensor like cameras
    timestamps: List[int]
    boxes: List[
        Optional[List[float]]
    ]  # x y width height; Can be None if cuboid can't be projected or if projection is actively deleted
    cuboids: Optional[List[List[float]]]  # dx dy dz px py pz roll pitch yaw


# Define CuboidAnnotation dataclass
@dataclass
class CuboidAnnotation:
    id: AnnotationID
    path: CuboidPath
    label: Optional[str] = None
    stationary: Optional[bool] = False
    type: Literal["cuboid"] = "cuboid"
    attributes: Optional[List[AttributePath]] = None
    activations: Optional[List[CuboidActivationPath]] = None
    projections: Optional[List[CuboidProjectionPath]] = None
    parent_id: Optional[AnnotationID] = None


# Define AttributesAnnotation dataclass
@dataclass
class AttributesAnnotation:
    id: AnnotationID
    type: Literal["attributes"] = "attributes"
    parent_id: Optional[AnnotationID] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class AnnotationPath:
    timestamps: List[int]
    values: List[List[float]]


@dataclass
class Point2DAnnotation:
    id: AnnotationID
    sensor_id: SensorID
    path: AnnotationPath  # values: [x, y]
    type: Literal["point_2d"] = "point_2d"
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = False
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class Box2DAnnotation:
    id: AnnotationID
    sensor_id: SensorID
    path: AnnotationPath  # values: [left, top, width, height]
    type: Literal["box_2d"] = "box_2d"
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = False
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


class Polyline2DAnnotation:
    id: AnnotationID
    sensor_id: SensorID
    path: AnnotationPath  # x_0, y_0, x_1, y_1, ..., x_n, y_n
    type: Literal["polyline_2d"] = "polyline_2d"
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = False
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class Polygon2DAnnotation:
    id: AnnotationID
    sensor_id: SensorID
    path: AnnotationPath  # x_0, y_0, x_1, y_1, ..., x_n, y_n
    type: Literal["polygon_2d"] = "polygon_2d"
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = False
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class PolygonAnnotation:
    id: AnnotationID
    sensor_id: Optional[SensorID]
    path: AnnotationPath  # x_0, y_0, z_0, x_1, y_1, z_1, ..., x_n, y_n, z_n
    type: Literal["polygon"] = "polygon"
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = False
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class TopdownPolygonAnnotation:
    id: AnnotationID
    sensor_id: Optional[SensorID]
    path: AnnotationPath  # x_0, y_0, z_0, x_1, y_1, z_1, ..., x_n, y_n, z_n
    type: Literal["polygon_topdown"] = "polygon_topdown"
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = True
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class PolylineAnnotation:
    id: AnnotationID
    sensor_id: Optional[SensorID]
    path: AnnotationPath  # x_0, y_0, z_0, x_1, y_1, z_1, ..., x_n, y_n, z_n
    type: Literal["polyline"] = "polyline"
    is_closed: Optional[bool] = None
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = False
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None

@dataclass
class TopdownPointAnnotation:
    id: AnnotationID
    sensor_id: Optional[SensorID]
    path: AnnotationPath  # x_0, y_0, z_0, x_1, y_1, z_1, ..., x_n, y_n, z_n
    type: Literal["point_topdown"] = "point_topdown"
    parent_id: Optional[AnnotationID] = None
    stationary: Literal[True] = True
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class PointAnnotation:
    id: AnnotationID
    sensor_id: Optional[SensorID]
    path: AnnotationPath  # x, y, z
    type: Literal["point"] = "point"
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = False
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class EventAnnotation:
    id: AnnotationID
    start: int
    type: Literal["event"] = "event"
    parent_id: Optional[AnnotationID] = None
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None
    duration: Optional[int] = None
    sensor_id: Optional[SensorID] = None


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
    type: Union[Literal["labeled_points"], Literal["point_segmentation"]] = "point_segmentation"
    parent_id: Optional[AnnotationID] = None


@dataclass
class LocalizationAdjustmentAnnotation:
    id: AnnotationID
    poses: PosePath
    type: Literal["localization_adjustment"] = "localization_adjustment"
    parent_id: Optional[AnnotationID] = None


@dataclass
class LinkAnnotation:
    id: AnnotationID
    sensor_id: Optional[SensorID]
    label: str
    is_bidirectional: bool
    from_id: AnnotationID
    to_id: AnnotationID
    type: Literal["link"] = "link"
    parent_id: Optional[AnnotationID] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class ObjectAnnotation:
    id: AnnotationID
    type: Literal["object"] = "object"
    parent_id: Optional[AnnotationID] = None
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


Sensor = Union[CameraSensor, LidarSensor, RadarSensor, OdometrySensor, PointsSensor]

Annotation = Union[
    CuboidAnnotation,
    AttributesAnnotation,
    Box2DAnnotation,
    Point2DAnnotation,
    Polyline2DAnnotation,
    Polygon2DAnnotation,
    PolygonAnnotation,
    TopdownPolygonAnnotation,
    TopdownPointAnnotation,
    PolylineAnnotation,
    PointAnnotation,
    LinkAnnotation,
    LabeledPointsAnnotation,
    LocalizationAdjustmentAnnotation,
    ObjectAnnotation,
    EventAnnotation,
]

# Define Scene dataclass


@dataclass
class Scene:
    version: Literal["1.0"] = "1.0"
    sensors: Optional[List[Sensor]] = None
    annotations: Optional[List[Annotation]] = None
    attributes: Optional[List[AttributePath]] = None
    time_offset: Optional[int] = None
    time_unit: Optional[Literal["microseconds", "nanoseconds"]] = "microseconds"
    metadata: Optional[Dict[str, Any]] = None
