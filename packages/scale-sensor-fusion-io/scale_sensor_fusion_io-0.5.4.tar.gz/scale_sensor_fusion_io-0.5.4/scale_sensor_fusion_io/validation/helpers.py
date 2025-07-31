from typing import (
    List,
    Optional,
    TypeVar,
    Callable,
)
from .error import ErrorDetails

import scale_sensor_fusion_io.validation.dacite_internal as dacite

T = TypeVar("T")


def convert_error(e: dacite.DaciteFieldError) -> ErrorDetails:
    return ErrorDetails(
        path=e.field_path.split(".") if e.field_path else [], errors=[str(e)]  # type: ignore
    )


def handle_dacite(
    fn: Callable[[], T], error_details: List[ErrorDetails]
) -> Optional[T]:
    """Handle dacite errors and aggregate errors"""
    try:
        return fn()
    except dacite.AggregatedError as e:
        error_details.extend([convert_error(err) for err in e.errors])
    except dacite.DaciteFieldError as e:
        error_details.append(convert_error(e))
    return None


def is_strictly_increasing(ts: List[int]) -> bool:
    """Check if a list of timestamps is strictly increasing"""
    return all(ts1 < ts2 for ts1, ts2 in zip(ts[:-1], ts[1:]))
