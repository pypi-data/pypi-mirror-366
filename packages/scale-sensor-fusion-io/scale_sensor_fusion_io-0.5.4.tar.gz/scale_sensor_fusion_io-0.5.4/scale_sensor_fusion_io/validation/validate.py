from dataclasses import asdict, dataclass
from typing import List, Tuple, Union, cast

import numpy as np
import numpy.typing as npt

from scale_sensor_fusion_io.models import (
    CameraDistortion,
    CameraIntrinsics,
    CameraSensor,
    LidarSensor,
    LidarSensorFrame,
    LidarSensorPoints,
    PosePath,
    RadarSensor,
    RadarSensorFrame,
    RadarSensorPoints,
    OdometrySensor,
    PointsSensor,
    Points,
    Scene,
    Sensor,
    SensorKind,
)

from .error import (
    DataValidationError,
    ErrorDetails,
    PathField,
    ValidationResult,
)
from .helpers import is_strictly_increasing

MICRO_IN_SEC = 1e6
MAX_FPS = 100
MIN_FPS = 1


def _handle_result(
    res: ValidationResult, error_details: List[ErrorDetails], path: List[PathField] = []
) -> None:
    if res:
        error_details.extend(
            res.details if not path else res.prepend_path(path).details
        )

    return None


def validate_pose_path(pose_path: PosePath) -> ValidationResult:
    error_details: List[ErrorDetails] = []

    pose_timestamps: List[int] = pose_path.index.tolist()
    _handle_result(
        validate_timestamps(pose_timestamps), error_details, path=["timestamps"]
    )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_timestamps(timestamps: List[int]) -> ValidationResult:
    error_details: List[ErrorDetails] = []
    if any(ts < 0 for ts in timestamps):
        error_details.append(
            ErrorDetails.from_msg(
                "timestamps must not be negative",
            )
        )
    if not is_strictly_increasing(timestamps):
        error_details.append(
            ErrorDetails.from_msg(
                "timestamps must be strictly increasing",
            )
        )

    max_ts_diff = MICRO_IN_SEC / MIN_FPS
    max_init_frame_ts = max_ts_diff * 100  # allow a padding of 100 frames
    if timestamps[0] > max_init_frame_ts:
        error_details.append(
            ErrorDetails.from_msg(
                f"timestamps must be normalized: {timestamps[0]} > {max_init_frame_ts}",
            )
        )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)
    return None


def validate_fps(timestamps: List[int], max_fps: int = MAX_FPS) -> ValidationResult:
    error_details: List[ErrorDetails] = []

    # compute approximate fps from timestamps
    if len(timestamps) < 2:
        return None

    avg_ts_diffs = cast(
        float, np.mean([t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])])
    )
    fps = float(MICRO_IN_SEC) / avg_ts_diffs if avg_ts_diffs != 0 else np.inf

    if fps > max_fps:
        error_details.append(
            ErrorDetails.from_msg(
                f"approximate fps is too high: {fps} > {max_fps}",
            )
        )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_points_positions(positions: npt.NDArray[np.float32]) -> ValidationResult:
    error_details: List[ErrorDetails] = []

    if positions.dtype != np.float32:
        error_details.append(
            ErrorDetails.from_msg(
                f"Positions must have dtype float32: is {positions.dtype}",
            )
        )

    shape = positions.shape if hasattr(positions, 'shape') else None
    if not shape or len(shape) != 2 or shape[1] != 3:
        error_details.append(
            ErrorDetails.from_msg(
                f"Positions must have shape (n, 3): is ({positions.shape})",
            )
        )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_points_colors(
    colors: npt.NDArray[np.uint8], expected_length: int
) -> ValidationResult:
    error_details: List[ErrorDetails] = []

    if colors.dtype != np.uint8:
        error_details.append(
            ErrorDetails.from_msg(
                f"Colors must have dtype uint8: is {colors.dtype}",
            )
        )

    shape = colors.shape if hasattr(colors, 'shape') else None
    if not shape or len(shape) != 2 or shape[1] != 3:
        error_details.append(
            ErrorDetails.from_msg(
                f"Colors must have shape (n, 3): is ({colors.shape})",
            )
        )

    if len(colors) != expected_length:
        error_details.append(
            ErrorDetails.from_msg(
                f"length of colors ({len(colors)}) should match length of positions: ({expected_length})",
            )
        )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_points_intensities(
    intensities: npt.NDArray[np.uint8], expected_length: int
) -> ValidationResult:
    error_details: List[ErrorDetails] = []

    if intensities.dtype != np.uint8:
        error_details.append(
            ErrorDetails.from_msg(
                f"Intensities must have dtype uint8: is {intensities.dtype}",
            )
        )

    if len(intensities.shape) != 1:
        error_details.append(
            ErrorDetails.from_msg(
                f"Intensities must have shape (n, 1): is ({intensities.shape})",
            )
        )

    if len(intensities) != expected_length:
        error_details.append(
            ErrorDetails.from_msg(
                f"length of intensities ({len(intensities)}) should match length of positions: ({expected_length})",
            )
        )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_points_timestamps(
    timestamps: Union[npt.NDArray[np.uint32], npt.NDArray[np.uint64]],
    expected_length: int,
) -> ValidationResult:
    error_details: List[ErrorDetails] = []

    if timestamps.dtype != np.uint32 and timestamps.dtype != np.uint64:
        error_details.append(
            ErrorDetails.from_msg(
                f"Timestamps must have dtype uint32 or uint64: is {timestamps.dtype}",
            )
        )

    shape: Tuple[int, ...] = tuple(timestamps.shape) 
    if not shape or len(shape) != 1:
        error_details.append(
            ErrorDetails.from_msg(
                f"Timestamps must have shape (n, 1): is ({getattr(timestamps, 'shape', None)})",
            )
        )

    ts_arr = np.asarray(timestamps)
    ts_length = len(ts_arr)
    if ts_length != expected_length:
        error_details.append(
            ErrorDetails.from_msg(
                f"length of timestamps ({ts_length}) should match length of positions: ({expected_length})",
            )
        )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_points_directions(
    directions: npt.NDArray[np.float32], expected_length: int
) -> ValidationResult:
    error_details: List[ErrorDetails] = []

    if directions.dtype != np.float32:
        error_details.append(
            ErrorDetails.from_msg(
                f"Directions must have dtype float32: is {directions.dtype}",
            )
        )

    shape = directions.shape if hasattr(directions, 'shape') else None
    if len(shape) != 2 or shape[1] != 3:
        error_details.append(
            ErrorDetails.from_msg(
                f"Directions must have shape (n, 3): is ({directions.shape})",
            )
        )

    if len(directions) != expected_length:
        error_details.append(
            ErrorDetails.from_msg(
                f"length of directions ({len(directions)}) should match length of positions: ({expected_length})",
            )
        )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_points_lengths(
    lengths: npt.NDArray[np.float32], expected_length: int
) -> ValidationResult:
    error_details: List[ErrorDetails] = []

    if lengths.dtype != np.float32:
        error_details.append(
            ErrorDetails.from_msg(
                f"Lengths must have dtype float32: is {lengths.dtype}",
            )
        )

    if len(lengths.shape) != 1:
        error_details.append(
            ErrorDetails.from_msg(
                f"Lengths must have shape (n, 1): is ({lengths.shape})",
            )
        )

    if len(lengths) != expected_length:
        error_details.append(
            ErrorDetails.from_msg(
                f"length of lengths ({len(lengths)}) should match length of positions: ({expected_length})",
            )
        )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_lidar(sensor: LidarSensor) -> ValidationResult:
    """Validate lidar sensor"""
    error_details: List[ErrorDetails] = []
    content_timestamps = [frame.timestamp for frame in sensor.frames]

    _handle_result(
        validate_timestamps(content_timestamps), error_details, path=["frames"]
    )
    _handle_result(validate_fps(content_timestamps), error_details, path=["frames"])

    # pose validation
    _handle_result(
        validate_pose_path(sensor.poses),
        error_details,
        path=["poses"],
    )

    for frame_num, frame in enumerate(sensor.frames):
        _handle_result(
            validate_points_positions(frame.points.positions),
            error_details,
            path=["frames", frame_num, "points", "positions"],
        )

        pos_length = len(frame.points.positions)
        if frame.points.colors is not None:
            _handle_result(
                validate_points_colors(frame.points.colors, expected_length=pos_length),
                error_details,
                path=["frames", frame_num, "points", "colors"],
            )

        if frame.points.intensities is not None:
            _handle_result(
                validate_points_intensities(
                    frame.points.intensities, expected_length=pos_length
                ),
                error_details,
                path=["frames", frame_num, "points", "intensities"],
            )

        if frame.points.timestamps is not None:
            _handle_result(
                validate_points_timestamps(
                    frame.points.timestamps, expected_length=pos_length
                ),
                error_details,
                path=["frames", frame_num, "points", "timestamps"],
            )

            next_frame_ts = (
                sensor.frames[frame_num + 1].timestamp
                if frame_num < len(sensor.frames) - 1
                else None
            )

            ts_array = np.asarray(frame.points.timestamps)
            min_points_ts = np.min(ts_array) if len(ts_array) > 0 else 0

            # NOTE: this is the correct validation, but it is too strict for now. We can add this back as a warning once we support warnings vs errors
            # if (
            #     frame.timestamp > min_points_ts
            #     or next_frame_ts
            #     and max_points_ts > next_frame_ts
            # ):
            #     error_details.append(
            #         ErrorDetails.from_msg(
            #             f"point timestamps (range {min_points_ts} -> {max_points_ts}) must be included within consecutive frame timestamps (range {frame.timestamp} -> {next_frame_ts})",
            #             path=["frames", frame_num, "points"],
            #         )
            #     )

            # Simpler check: frame timestamp must be less the min point timestamp
            if frame.timestamp > min_points_ts:
                error_details.append(
                    ErrorDetails.from_msg(
                        f"frame timestamp ({frame.timestamp}) must be less than min point timestamp ({min_points_ts})",
                        path=["frames", frame_num, "points", "timestamps"],
                    )
                )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_radar(sensor: RadarSensor) -> ValidationResult:
    """Validate radar sensor"""
    error_details: List[ErrorDetails] = []
    content_timestamps = [frame.timestamp for frame in sensor.frames]

    _handle_result(
        validate_timestamps(content_timestamps), error_details, path=["frames"]
    )
    _handle_result(validate_fps(content_timestamps), error_details, path=["frames"])

    # pose validation
    _handle_result(
        validate_pose_path(sensor.poses),
        error_details,
        path=["poses"],
    )

    for frame_num, frame in enumerate(sensor.frames):
        _handle_result(
            validate_points_positions(frame.points.positions),
            error_details,
            path=["frames", frame_num, "points", "positions"],
        )

        pos_length = len(frame.points.positions)
        if frame.points.directions is not None:
            _handle_result(
                validate_points_directions(
                    frame.points.directions, expected_length=pos_length
                ),
                error_details,
                path=["frames", frame_num, "points", "directions"],
            )

        if frame.points.lengths is not None:
            _handle_result(
                validate_points_lengths(
                    frame.points.lengths, expected_length=pos_length
                ),
                error_details,
                path=["frames", frame_num, "points", "lengths"],
            )

        if frame.points.timestamps is not None:
            _handle_result(
                validate_points_timestamps(
                    frame.points.timestamps, expected_length=pos_length
                ),
                error_details,
                path=["frames", frame_num, "points", "timestamps"],
            )

            next_frame_ts = (
                sensor.frames[frame_num + 1].timestamp
                if frame_num < len(sensor.frames) - 1
                else None
            )

            ts_array = np.asarray(frame.points.timestamps)
            min_points_ts = np.min(ts_array) if len(ts_array) > 0 else 0

            # NOTE: this is the correct validation, but it is too strict for now. We can add this back as a warning once we support warnings vs errors
            # if (
            #     frame.timestamp > min_points_ts
            #     or next_frame_ts
            #     and max_points_ts > next_frame_ts
            # ):
            #     error_details.append(
            #         ErrorDetails.from_msg(
            #             f"point timestamps (range {min_points_ts} -> {max_points_ts}) must be included within consecutive frame timestamps (range {frame.timestamp} -> {next_frame_ts})",
            #             path=["frames", frame_num, "points"],
            #         )
            #     )

            # Simpler check: frame timestamp must be less the min point timestamp
            if frame.timestamp > min_points_ts:
                error_details.append(
                    ErrorDetails.from_msg(
                        f"frame timestamp ({frame.timestamp}) must be less than min point timestamp ({min_points_ts})",
                        path=["frames", frame_num, "points", "timestamps"],
                    )
                )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_camera(sensor: CameraSensor) -> ValidationResult:
    """Validate camera sensor"""
    error_details: List[ErrorDetails] = []

    # camera content
    content_timestamps: List[int] = []
    content_timestamps_path: List[PathField] = []
    if sensor.video:
        content_timestamps = sensor.video.timestamps
        content_timestamps_path = ["video"]
    elif sensor.images:
        content_timestamps = [img.timestamp for img in sensor.images]
        content_timestamps_path = ["images"]
    else:
        error_details.append(
            ErrorDetails.from_msg('Exactly one of "images" or "video" expected')
        )

    _handle_result(
        validate_timestamps(content_timestamps),
        error_details,
        path=content_timestamps_path,
    )
    _handle_result(
        validate_fps(content_timestamps),
        error_details,
        path=content_timestamps_path,
    )

    # pose validation
    _handle_result(validate_pose_path(sensor.poses), error_details, path=["poses"])

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_points_sensor(sensor: PointsSensor) -> ValidationResult:
    # pose validation
    error_details: List[ErrorDetails] = []

    _handle_result(
        validate_points_positions(sensor.points.positions),
        error_details,
        path=["points", "positions"],
    )

    if sensor.points.colors is not None:
        _handle_result(
            validate_points_colors(
                sensor.points.colors, expected_length=len(sensor.points.positions)
            ),
            error_details,
            path=["points", "colors"],
        )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_odometer(sensor: OdometrySensor) -> ValidationResult:
    # pose validation
    error_details: List[ErrorDetails] = []

    _handle_result(validate_pose_path(sensor.poses), error_details, path=["poses"])

    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_sensor(sensor: Sensor) -> ValidationResult:
    error_details: List[ErrorDetails] = []
    if sensor.type is SensorKind.Camera:
        _handle_result(validate_camera(sensor), error_details)
    elif sensor.type is SensorKind.Lidar:
        _handle_result(validate_lidar(sensor), error_details)
    elif sensor.type is SensorKind.Radar:
        _handle_result(validate_radar(sensor), error_details)
    elif sensor.type is SensorKind.Points:
        _handle_result(validate_points_sensor(sensor), error_details)
    elif sensor.type is SensorKind.Odometer:
        _handle_result(validate_odometer(sensor), error_details)
    else:
        error_details.append(
            ErrorDetails(
                path=["type"], errors=[f"Invalid sensor type provided: {sensor.type}"]
            )
        )
    if len(error_details) > 0:
        return DataValidationError(details=error_details)

    return None


def validate_scene(scene: Scene) -> ValidationResult:
    """Validate scene"""
    error_details: List[ErrorDetails] = []
    if scene.sensors:
        for sensor in scene.sensors:
            _handle_result(
                validate_sensor(sensor),
                error_details,
                path=["sensors", str(sensor.id)],
            )

        if len(scene.sensors) != len(set([sensor.id for sensor in scene.sensors])):
            error_details.append(
                ErrorDetails.from_msg("Sensor ids must be unique", path=["sensors"])
            )

    if scene.time_unit != "microseconds":
        error_details.append(
            ErrorDetails.from_msg(
                f"Invalid time unit provided: {scene.time_unit}. Expected: microseconds"
            )
        )

    if scene.time_offset is not None and scene.time_offset < 0:
        error_details.append(
            ErrorDetails.from_msg("Scene timestamp must not be negative")
        )

    if len(error_details) > 0:
        return DataValidationError(details=error_details)
    return None
