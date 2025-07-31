import pprint
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Callable, Generic, List, Literal, Optional, TypeVar, Union

import numpy as np
import scale_sensor_fusion_io.validation.dacite_internal as _dacite
from scale_json_binary import read_file
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
    Scene,
    Sensor,
)
from scale_sensor_fusion_io.spec import SFS
from scale_sensor_fusion_io.validation.error import (
    ErrorDetails,
    ParseError,
    ParseResult,
    ParseSuccess,
    PathField,
    ValidationResult,
)
from scale_sensor_fusion_io.validation.helpers import (
    convert_error,
    handle_dacite,
    is_strictly_increasing,
)
from typing_extensions import TypeAlias

CFG = _dacite.Config(cast=[Enum, tuple])

_T = TypeVar("_T")


"""Parse and validate a sfs file"""


def _handle_result(
    res: ParseResult[_T], error_details: List[ErrorDetails], path: List[PathField] = []
) -> Optional[_T]:
    if res.success:
        return res.data
    else:
        error_details.extend(
            res.details if not path else res.prepend_path(path).details
        )
        return None


def parse_radar(sensor: dict) -> ParseResult[SFS.RadarSensor]:
    error_details: List[ErrorDetails] = []

    parsed_sensor = handle_dacite(
        lambda: _dacite.from_dict(
            data_class=SFS.RadarSensor,
            data=sensor,
            config=CFG,
        ),
        error_details,
    )

    if parsed_sensor:
        if len(parsed_sensor.frames) <= 0:
            error_details.append(
                ErrorDetails(path=["frames"], errors=["Must have at least one frame"])
            )

        for idx, frame in enumerate(parsed_sensor.frames):
            """
            When reading via dacite, the numpy arrays aren't correctly shaped (since that's not included in the typedef)
            Thus, we reshape all fields here
            """
            frame.points.positions = frame.points.positions.reshape((-1, 3))
            frame.points.directions = (
                frame.points.directions.reshape((-1, 3))
                if frame.points.directions is not None
                else None
            )
            if (
                frame.points.timestamps is not None
                and frame.points.timestamps.dtype == np.uint64
            ):
                error_details.append(
                    ErrorDetails(
                        path=["frames", idx, "points", "timestamps"],
                        errors=["Uint64 timestamps are not supported yet"],
                    )
                )

    if len(error_details) > 0:
        return ParseError(details=error_details)

    assert parsed_sensor is not None
    return ParseSuccess(data=parsed_sensor)


def parse_lidar(sensor: dict) -> ParseResult[SFS.LidarSensor]:
    error_details: List[ErrorDetails] = []

    parsed_sensor = handle_dacite(
        lambda: _dacite.from_dict(
            data_class=SFS.LidarSensor,
            data=sensor,
            config=CFG,
        ),
        error_details,
    )

    if parsed_sensor:
        if len(parsed_sensor.frames) <= 0:
            error_details.append(
                ErrorDetails(path=["frames"], errors=["Must have at least one frame"])
            )

        for idx, frame in enumerate(parsed_sensor.frames):
            """
            When reading via dacite, the numpy arrays aren't correctly shaped (since that's not included in the typedef)
            Thus, we reshape all fields here
            """
            frame.points.positions = frame.points.positions.reshape((-1, 3))
            frame.points.colors = (
                frame.points.colors.reshape((-1, 3))
                if frame.points.colors is not None
                else None
            )
            if (
                frame.points.timestamps is not None
                and frame.points.timestamps.dtype == np.uint64
            ):
                error_details.append(
                    ErrorDetails(
                        path=["frames", idx, "points", "timestamps"],
                        errors=["Uint64 timestamps are not supported yet"],
                    )
                )

    if len(error_details) > 0:
        return ParseError(details=error_details)

    assert parsed_sensor is not None
    return ParseSuccess(data=parsed_sensor)


def parse_sensor(sensor: dict) -> ParseResult[SFS.Sensor]:
    error_details: List[ErrorDetails] = []

    # type
    sensor_type = sensor.get("type")
    if not sensor_type:
        error_details.append(ErrorDetails.missing_field("type"))

    parsed_sensor: Optional[SFS.Sensor] = None
    if sensor_type == "camera":
        parsed_sensor = handle_dacite(
            lambda: _dacite.from_dict(
                data_class=SFS.CameraSensor,
                data=sensor,
                config=CFG,
            ),
            error_details,
        )
    elif sensor_type == "lidar":
        parsed_sensor = _handle_result(parse_lidar(sensor), error_details)
    elif sensor_type == "radar":
        parsed_sensor = _handle_result(parse_radar(sensor), error_details)
    else:
        error_details.append(
            ErrorDetails(
                path=["type"], errors=[f"Invalid sensor type provided: {sensor_type}"]
            )
        )

    if len(error_details) > 0:
        return ParseError(details=error_details)

    assert parsed_sensor is not None
    return ParseSuccess(data=parsed_sensor)


def parse_scene_as_sfs(raw_data: dict) -> ParseResult[SFS.Scene]:
    """
    Parse raw dict as SFS.Scene

    Few notes:
      * We use a modified version of dacite to allow for aggregating errors instead of failing fast
      * We also don't run _dacite.from_dict on the scene object directly since it can't handle union types very elegantly currently
    """
    error_details: List[ErrorDetails] = []

    # version
    version = raw_data.get("version")
    if version is None:
        return ParseError.missing_field("version")

    if not raw_data["version"].startswith("1.0") and not raw_data["version"].startswith(
        "5.1"
    ):
        return ParseError.from_msg(
            f"Invalid version provided: {raw_data['version']}", path=["version"]
        )

    # sensors
    sensors = []
    _sensors = raw_data.get("sensors")
    if _sensors:
        if type(_sensors) != list:
            return ParseError.from_msg("Sensors must be a list", path=["sensors"])

        for idx, sensor in enumerate(_sensors):
            sensor = _handle_result(
                parse_sensor(sensor), error_details, path=["sensors", idx]
            )
            if sensor:
                sensors.append(sensor)

    # time_offset
    fields = SFS.Scene.__dataclass_fields__
    time_offset = handle_dacite(
        lambda: _dacite.cast_field(raw_data, field=fields["time_offset"], config=CFG),  # type: ignore
        error_details,
    )

    # time_unit
    time_unit = handle_dacite(
        lambda: _dacite.cast_field(raw_data, field=fields["time_unit"], config=CFG),  # type: ignore
        error_details,
    )

    # Additional scene level validations
    if len(error_details) == 0:
        scene = SFS.Scene(sensors=sensors, time_offset=time_offset, time_unit=time_unit)

        return ParseSuccess(data=scene)

    return ParseError(details=error_details)
    pass
