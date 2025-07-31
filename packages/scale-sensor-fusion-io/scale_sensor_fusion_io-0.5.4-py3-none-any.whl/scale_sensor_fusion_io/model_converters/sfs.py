from dataclasses import asdict, fields
from typing import List, Optional

import numpy as np
from scale_sensor_fusion_io.models import (
    Annotation,
    AttributePath,
    AttributesAnnotation,
    Box2DAnnotation,
    Box2DPath,
    CameraDistortion,
    CameraIntrinsics,
    CameraSensor,
    CameraSensorImage,
    CameraSensorVideo,
    CuboidActivationPath,
    CuboidAnnotation,
    CuboidPath,
    CuboidProjectionPath,
    EventAnnotation,
    LabeledPoint,
    LabeledPointsAnnotation,
    LidarSensor,
    LidarSensorFrame,
    LidarSensorPoints,
    LocalizationAdjustmentAnnotation,
    ObjectAnnotation,
    PolygonAnnotation,
    TopdownPolygonAnnotation,
    PolygonPath,
    TopdownPolygonPath,
    PolylineAnnotation,
    PolylinePath,
    PosePath,
    RadarSensor,
    RadarSensorFrame,
    RadarSensorPoints,
    Scene,
    Sensor,
)
from scale_sensor_fusion_io.spec import SFS


def from_lidarpoints_sfs(points: SFS.LidarSensorPoints) -> LidarSensorPoints:
    return LidarSensorPoints(
        positions=points.positions.reshape(-1, 3),
        colors=points.colors.reshape(-1, 3) if points.colors is not None else None,
        intensities=points.intensities,
        timestamps=points.timestamps if points.timestamps is not None else None,
    )


def to_lidarpoints_sfs(points: LidarSensorPoints) -> SFS.LidarSensorPoints:
    return SFS.LidarSensorPoints(
        positions=points.positions.reshape(-1, 3),
        colors=points.colors.reshape(-1, 3) if points.colors is not None else None,
        intensities=points.intensities,
        timestamps=points.timestamps,
    )


def from_radarpoints_sfs(points: SFS.RadarSensorPoints) -> RadarSensorPoints:
    return RadarSensorPoints(
        positions=points.positions.reshape(-1, 3),
        directions=(
            points.directions.reshape(-1, 3) if points.directions is not None else None
        ),
        timestamps=points.timestamps if points.timestamps is not None else None,
    )


def to_radarpoints_sfs(points: RadarSensorPoints) -> SFS.RadarSensorPoints:
    return SFS.RadarSensorPoints(
        positions=points.positions.reshape(-1, 3),
        directions=(
            points.directions.reshape(-1, 3) if points.directions is not None else None
        ),
        timestamps=points.timestamps,
    )


def from_pose_sfs(posePath: SFS.PosePath) -> PosePath:
    timestamps = np.array(t for t in posePath.timestamps)
    values = np.vstack([v for v in posePath.values])

    return PosePath(data=values, index=timestamps)


def to_pose_sfs(poses: PosePath) -> SFS.PosePath:
    return SFS.PosePath(
        timestamps=poses.index.tolist(),
        values=poses.values.tolist(),
    )


def from_camera_timestamp(camera_sensor: SFS.CameraSensor) -> List[int]:
    if camera_sensor.images:
        return [i.timestamp for i in camera_sensor.images]
    elif camera_sensor.video:
        return camera_sensor.video.timestamps
    else:
        raise Exception("Camera sensor has no timestamp info")


def from_intrinsics_sfs(intrinsics: SFS.CameraIntrinsics) -> CameraIntrinsics:
    return CameraIntrinsics(
        fx=intrinsics.fx,
        fy=intrinsics.fy,
        cx=intrinsics.cx,
        cy=intrinsics.cy,
        width=intrinsics.width,
        height=intrinsics.height,
        distortion=from_distortion_sfs(intrinsics.distortion),
    )


def to_intrinsics_sfs(intrinsics: CameraIntrinsics) -> SFS.CameraIntrinsics:
    return SFS.CameraIntrinsics(
        fx=intrinsics.fx,
        fy=intrinsics.fy,
        cx=intrinsics.cx,
        cy=intrinsics.cy,
        width=intrinsics.width,
        height=intrinsics.height,
        distortion=to_distortion_sfs(intrinsics.distortion),
    )


"""
NOTE: The distortion conversion does not need to keep track of the order of the
coefficients since this is managed by the dataclass themselves. However this implies
that 1) distortion parameters must remain dataclasses and 2) the ordering of the
variables matters.
"""


def from_distortion_sfs(
    distortion: Optional[SFS.CameraDistortion],
) -> Optional[CameraDistortion]:
    if distortion is None or not distortion.model:
        return None

    return CameraDistortion.from_values(
        model=distortion.model, values=distortion.params
    )


def to_distortion_sfs(
    distortion: Optional[CameraDistortion],
) -> Optional[SFS.CameraDistortion]:
    if not distortion or not distortion.model:
        return None

    # dataclasses.asdict may not preserve order so use dataclasses.fields instead
    params = [
        getattr(distortion.params, k.name)
        for k in fields(distortion.params)
        if k.name != "model"
    ]
    return SFS.CameraDistortion(model=distortion.model.value, params=params)


def from_attribute_paths_sfs(
    attributes: Optional[List[SFS.AttributePath]],
) -> Optional[List[AttributePath]]:
    """Convert a list of SFS.AttributePath into SFIO.AttributePath"""

    return (
        [
            AttributePath(
                name=attribute.name,
                timestamps=attribute.timestamps,
                values=attribute.values,
                sensor_id=attribute.sensor_id,
                static=attribute.static,
            )
            for attribute in attributes
        ]
        if attributes
        else None
    )


def to_attribute_paths_sfs(
    attributes: Optional[List[AttributePath]],
) -> Optional[List[SFS.AttributePath]]:
    """Convert a list of SFIO.AttributePath into SFS.AttributePath"""

    return (
        [
            SFS.AttributePath(
                name=attribute.name,
                timestamps=attribute.timestamps,
                values=attribute.values,
                sensor_id=attribute.sensor_id,
                static=attribute.static,
            )
            for attribute in attributes
        ]
        if attributes
        else None
    )


def from_sensors_sfs(sensors: Optional[List[SFS.Sensor]]) -> Optional[List[Sensor]]:
    """Convert a list of SFS.Sensor into SFIO.Sensor"""

    if not sensors:
        return None
    ret: List[Sensor] = []
    for sensor in sensors:
        if isinstance(sensor, SFS.LidarSensor):
            lidar_sensor = sensor
            poses = from_pose_sfs(lidar_sensor.poses)
            frames = [
                LidarSensorFrame(
                    timestamp=int(f.timestamp), points=from_lidarpoints_sfs(f.points)
                )
                for f in lidar_sensor.frames
            ]
            l_sensor = LidarSensor(id=lidar_sensor.id, poses=poses, frames=frames)
            ret.append(l_sensor)
        elif isinstance(sensor, SFS.RadarSensor):
            radar_sensor = sensor
            r_poses = from_pose_sfs(radar_sensor.poses)

            r_frames = [
                RadarSensorFrame(
                    timestamp=int(f.timestamp), points=from_radarpoints_sfs(f.points)
                )
                for f in radar_sensor.frames
            ]
            r_sensor = RadarSensor(id=radar_sensor.id, poses=r_poses, frames=r_frames)
            ret.append(r_sensor)
        elif isinstance(sensor, SFS.CameraSensor):
            camera_sensor = sensor
            c_poses = from_pose_sfs(camera_sensor.poses)
            intrinsics = from_intrinsics_sfs(camera_sensor.intrinsics)
            video, images = None, None

            # sfio and SFS video/images are exactly the same but separated
            # for spec purposes
            if camera_sensor.video:
                video = CameraSensorVideo(**asdict(camera_sensor.video))

            if camera_sensor.images:
                images = [CameraSensorImage(**asdict(i)) for i in camera_sensor.images]

            ret.append(
                CameraSensor(
                    id=camera_sensor.id,
                    poses=c_poses,
                    intrinsics=intrinsics,
                    video=video,
                    images=images,
                )
            )
    return ret


def to_sensors_sfs(sensors: Optional[List[Sensor]]) -> Optional[List[SFS.Sensor]]:
    """Convert a list of SFIO.Sensor into SFS.Sensor"""

    if not sensors:
        return None
    ret: List[SFS.Sensor] = []
    for sensor in sensors:
        if isinstance(sensor, CameraSensor):
            video, images = None, None

            if sensor.video:
                video = SFS.CameraSensorVideo(**asdict(sensor.video))

            if sensor.images:
                images = [SFS.CameraSensorImage(**asdict(i)) for i in sensor.images]

            ret.append(
                SFS.CameraSensor(
                    id=sensor.id,
                    poses=to_pose_sfs(sensor.poses),
                    intrinsics=to_intrinsics_sfs(sensor.intrinsics),
                    video=video,
                    images=images,
                )
            )
        elif isinstance(sensor, RadarSensor):
            ret.append(
                SFS.RadarSensor(
                    id=sensor.id,
                    poses=to_pose_sfs(sensor.poses),
                    frames=[
                        SFS.RadarSensorFrame(
                            timestamp=frame.timestamp,
                            points=to_radarpoints_sfs(frame.points),
                        )
                        for frame in sensor.frames
                    ],
                )
            )
        elif isinstance(sensor, LidarSensor):
            ret.append(
                SFS.LidarSensor(
                    id=sensor.id,
                    poses=to_pose_sfs(sensor.poses),
                    frames=[
                        SFS.LidarSensorFrame(
                            timestamp=frame.timestamp,
                            points=to_lidarpoints_sfs(frame.points),
                        )
                        for frame in sensor.frames
                    ],
                )
            )
    return ret


def from_annotations_sfs(
    annotations: Optional[List[SFS.Annotation]],
) -> Optional[List[Annotation]]:
    """Convert a list of SFS.Annotation into SFIO.Annotation"""

    if not annotations:
        return None
    ret: List[Annotation] = []
    for annotation in annotations:
        if isinstance(annotation, SFS.AttributesAnnotation):
            ret.append(
                AttributesAnnotation(
                    id=annotation.id,
                    parent_id=annotation.parent_id,
                    attributes=from_attribute_paths_sfs(annotation.attributes),
                )
            )
        elif isinstance(annotation, SFS.Box2DAnnotation):
            ret.append(
                Box2DAnnotation(
                    id=annotation.id,
                    sensor_id=annotation.sensor_id,
                    path=Box2DPath(
                        timestamps=annotation.path.timestamps,
                        values=annotation.path.values,
                    ),
                    parent_id=annotation.parent_id,
                    stationary=annotation.stationary,
                    label=annotation.label,
                    attributes=from_attribute_paths_sfs(annotation.attributes),
                )
            )
        elif isinstance(annotation, SFS.CuboidAnnotation):
            ret.append(
                CuboidAnnotation(
                    id=annotation.id,
                    path=CuboidPath(
                        # from dx, dy, dz, x, y, z, roll, pitch, yaw
                        # to   x, y, z, yaw, pitch, roll, dx, dy, dz
                        data=[
                            row[3:6] + row[8:5:-1] + row[0:3]
                            for row in annotation.path.values
                        ],
                        index=annotation.path.timestamps,
                    ),
                    label=annotation.label,
                    stationary=annotation.stationary,
                    attributes=from_attribute_paths_sfs(annotation.attributes),
                    activations=(
                        [
                            CuboidActivationPath(
                                sensor_id=activation.sensor_id,
                                timestamps=activation.timestamps,
                                durations=activation.durations,
                                cuboids=(
                                    # from dx, dy, dz, x, y, z, roll, pitch, yaw
                                    # to   x, y, z, yaw, pitch, roll, dx, dy, dz
                                    [
                                        row[3:6] + row[8:5:-1] + row[0:3]
                                        for row in activation.cuboids
                                    ]
                                    if activation.cuboids
                                    else None
                                ),
                            )
                            for activation in annotation.activations
                        ]
                        if annotation.activations
                        else None
                    ),
                    projections=(
                        [
                            CuboidProjectionPath(
                                sensor_id=projection.sensor_id,
                                timestamps=projection.timestamps,
                                boxes=projection.boxes,
                                cuboids=projection.cuboids,
                            )
                            for projection in annotation.projections
                        ]
                        if annotation.projections
                        else None
                    ),
                    parent_id=annotation.parent_id,
                )
            )
        elif isinstance(annotation, SFS.EventAnnotation):
            ret.append(
                EventAnnotation(
                    id=annotation.id,
                    start=annotation.start,
                    parent_id=annotation.parent_id,
                    label=annotation.label,
                    attributes=from_attribute_paths_sfs(annotation.attributes),
                    duration=annotation.duration,
                    sensor_id=annotation.sensor_id,
                )
            )
        elif isinstance(annotation, SFS.LabeledPointsAnnotation):
            ret.append(
                LabeledPointsAnnotation(
                    id=annotation.id,
                    label=annotation.label,
                    labeled_points=[
                        LabeledPoint(
                            sensor_id=lp.sensor_id,
                            point_ids=lp.point_ids,
                            sensor_frame=lp.sensor_frame,
                        )
                        for lp in annotation.labeled_points
                    ],
                    is_instance=annotation.is_instance,
                    parent_id=annotation.parent_id,
                )
            )
        elif isinstance(annotation, SFS.LocalizationAdjustmentAnnotation):
            ret.append(
                LocalizationAdjustmentAnnotation(
                    id=annotation.id,
                    poses=from_pose_sfs(annotation.poses),
                    parent_id=annotation.parent_id,
                )
            )
        elif isinstance(annotation, SFS.ObjectAnnotation):
            ret.append(
                ObjectAnnotation(
                    id=annotation.id,
                    parent_id=annotation.parent_id,
                    label=annotation.label,
                    attributes=from_attribute_paths_sfs(annotation.attributes),
                )
            )
        elif isinstance(annotation, SFS.Polygon2DAnnotation):
            ret.append(
                PolygonAnnotation(
                    id=annotation.id,
                    sensor_id=annotation.sensor_id,
                    path=PolygonPath(
                        timestamps=annotation.path.timestamps,
                        values=annotation.path.values,
                    ),
                    parent_id=annotation.parent_id,
                    stationary=annotation.stationary,
                    label=annotation.label,
                    attributes=from_attribute_paths_sfs(annotation.attributes),
                )
            )
        elif isinstance(annotation, SFS.TopdownPolygonAnnotation):
            ret.append(
                TopdownPolygonAnnotation(
                    id=annotation.id,
                    sensor_id=annotation.sensor_id,
                    path=TopdownPolygonPath(
                        timestamps=annotation.path.timestamps,
                        values=annotation.path.values,
                    ),
                    parent_id=annotation.parent_id,
                    stationary=annotation.stationary,
                    label=annotation.label,
                    attributes=from_attribute_paths_sfs(annotation.attributes),
                )
            )
        elif isinstance(annotation, SFS.PolylineAnnotation):
            ret.append(
                PolylineAnnotation(
                    id=annotation.id,
                    sensor_id=annotation.sensor_id,
                    path=PolylinePath(
                        timestamps=annotation.path.timestamps,
                        values=annotation.path.values,
                    ),
                    is_closed=annotation.is_closed,
                    parent_id=annotation.parent_id,
                    stationary=annotation.stationary,
                    label=annotation.label,
                    attributes=from_attribute_paths_sfs(annotation.attributes),
                )
            )
        else:
            raise TypeError(f"Annotation type {type(annotation)} is not implemented")
    return ret


def to_annotations_sfs(
    annotations: Optional[List[Annotation]],
) -> Optional[List[SFS.Annotation]]:
    """Convert a list of SFIO.Annotation into SFS.Annotation"""

    if not annotations:
        return None
    ret: List[SFS.Annotation] = []
    for annotation in annotations:
        if isinstance(annotation, AttributesAnnotation):
            ret.append(
                SFS.AttributesAnnotation(
                    id=annotation.id,
                    parent_id=annotation.parent_id,
                    attributes=to_attribute_paths_sfs(annotation.attributes),
                )
            )
        elif isinstance(annotation, Box2DAnnotation):
            ret.append(
                SFS.Box2DAnnotation(
                    id=annotation.id,
                    sensor_id=annotation.sensor_id,
                    path=SFS.AnnotationPath(
                        timestamps=annotation.path.timestamps,
                        values=annotation.path.values,
                    ),
                    parent_id=annotation.parent_id,
                    stationary=annotation.stationary,
                    label=annotation.label,
                    attributes=to_attribute_paths_sfs(annotation.attributes),
                )
            )
        elif isinstance(annotation, CuboidAnnotation):
            ret.append(
                SFS.CuboidAnnotation(
                    id=annotation.id,
                    path=SFS.CuboidPath(
                        timestamps=annotation.path.index.tolist(),
                        values=annotation.path[
                            ["dx", "dy", "dz", "x", "y", "z", "roll", "pitch", "yaw"]
                        ].values.tolist(),
                    ),
                    label=annotation.label,
                    stationary=annotation.stationary,
                    attributes=to_attribute_paths_sfs(annotation.attributes),
                    activations=(
                        [
                            SFS.CuboidActivationPath(
                                sensor_id=activation.sensor_id,
                                timestamps=activation.timestamps,
                                durations=activation.durations,
                                cuboids=(
                                    # from x, y, z, yaw, pitch, roll, dx, dy, dz
                                    # to   dx, dy, dz, x, y, z, roll, pitch, yaw
                                    [
                                        row[6:9] + row[0:3] + row[5:2:-1]
                                        for row in activation.cuboids
                                    ]
                                    if activation.cuboids
                                    else None
                                ),
                            )
                            for activation in annotation.activations
                        ]
                        if annotation.activations
                        else None
                    ),
                    projections=(
                        [
                            SFS.CuboidProjectionPath(
                                sensor_id=projection.sensor_id,
                                timestamps=projection.timestamps,
                                boxes=projection.boxes,
                                cuboids=projection.cuboids,
                            )
                            for projection in annotation.projections
                        ]
                        if annotation.projections
                        else None
                    ),
                    parent_id=annotation.parent_id,
                )
            )
        elif isinstance(annotation, EventAnnotation):
            ret.append(
                SFS.EventAnnotation(
                    id=annotation.id,
                    start=annotation.start,
                    parent_id=annotation.parent_id,
                    label=annotation.label,
                    attributes=to_attribute_paths_sfs(annotation.attributes),
                    duration=annotation.duration,
                    sensor_id=annotation.sensor_id,
                )
            )
        elif isinstance(annotation, LabeledPointsAnnotation):
            ret.append(
                SFS.LabeledPointsAnnotation(
                    id=annotation.id,
                    label=annotation.label,
                    labeled_points=[
                        SFS.LabeledPoint(
                            sensor_id=lp.sensor_id,
                            point_ids=lp.point_ids,
                            sensor_frame=lp.sensor_frame,
                        )
                        for lp in annotation.labeled_points
                    ],
                    is_instance=annotation.is_instance,
                    parent_id=annotation.parent_id,
                )
            )
        elif isinstance(annotation, LocalizationAdjustmentAnnotation):
            ret.append(
                SFS.LocalizationAdjustmentAnnotation(
                    id=annotation.id,
                    poses=to_pose_sfs(annotation.poses),
                    parent_id=annotation.parent_id,
                )
            )
        elif isinstance(annotation, ObjectAnnotation):
            ret.append(
                SFS.ObjectAnnotation(
                    id=annotation.id,
                    parent_id=annotation.parent_id,
                    label=annotation.label,
                    attributes=to_attribute_paths_sfs(annotation.attributes),
                )
            )
        elif isinstance(annotation, PolygonAnnotation):
            ret.append(
                SFS.Polygon2DAnnotation(
                    id=annotation.id,
                    sensor_id=annotation.sensor_id,
                    path=SFS.AnnotationPath(
                        timestamps=annotation.path.timestamps,
                        values=annotation.path.values,
                    ),
                    parent_id=annotation.parent_id,
                    stationary=annotation.stationary,
                    label=annotation.label,
                    attributes=to_attribute_paths_sfs(annotation.attributes),
                )
            )
        elif isinstance(annotation, TopdownPolygonAnnotation):
            ret.append(
                SFS.TopdownPolygonAnnotation(
                    id=annotation.id,
                    sensor_id=annotation.sensor_id,
                    path=SFS.AnnotationPath(
                        timestamps=annotation.path.timestamps,
                        values=annotation.path.values,
                    ),
                    parent_id=annotation.parent_id,
                    stationary=annotation.stationary,
                    label=annotation.label,
                    attributes=to_attribute_paths_sfs(annotation.attributes),
                )
            )
        elif isinstance(annotation, PolylineAnnotation):
            ret.append(
              SFS.PolylineAnnotation(
                id=annotation.id,
                path=SFS.AnnotationPath(
                    timestamps=annotation.path.timestamps,
                    values=annotation.path.values,
                ),
                is_closed=annotation.is_closed,
                stationary=annotation.stationary,
                label=annotation.label,
                sensor_id=annotation.sensor_id,
                attributes=to_attribute_paths_sfs(annotation.attributes),
              )
            )
        else:
          raise TypeError(f"Annotation type {type(annotation)} is not implemented")
          
    return ret


def from_scene_spec_sfs(scene: SFS.Scene) -> Scene:
    """Convert SFS.Scene into SFIO.Scene"""

    return Scene(
        sensors=from_sensors_sfs(scene.sensors),
        annotations=from_annotations_sfs(scene.annotations),
        attributes=from_attribute_paths_sfs(scene.attributes),
        time_offset=scene.time_offset,
        time_unit=scene.time_unit,
        metadata=scene.metadata,
    )


def to_scene_spec_sfs(scene: Scene) -> SFS.Scene:
    """Convert SFIO.Scene into SFS.Scene"""

    return SFS.Scene(
        sensors=to_sensors_sfs(scene.sensors),
        annotations=to_annotations_sfs(scene.annotations),
        attributes=to_attribute_paths_sfs(scene.attributes),
        time_offset=scene.time_offset,
        time_unit=scene.time_unit,
        metadata=scene.metadata,
    )
