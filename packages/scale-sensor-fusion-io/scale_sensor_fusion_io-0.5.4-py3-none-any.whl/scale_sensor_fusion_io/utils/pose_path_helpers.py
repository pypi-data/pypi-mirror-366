"""Additional functionality for using PosePath."""

from typing import Optional, Union

import numpy as np
import numpy.typing as npt
import pandas as pd

from scale_sensor_fusion_io import FillValue, PosePath
from scale_sensor_fusion_io.utils.pose_helpers import transform_points


def apply_interpolated_transform_to_points(
    points: npt.ArrayLike,
    timestamps: npt.ArrayLike,
    pose_path_adjustment: PosePath,
    resolution: Optional[Union[float, int]] = None,
    extrapolation_strategy: Optional[str] = None,
) -> npt.NDArray:
    """
    Applies interpolated transformations from the given PosePath to the given points based on their
    corresponding timestamps and the specified resolution.

    This method groups points that have timestamps closer than the provided resolution value and
    applies the same transformation to each point within the group, improving performance by
    reducing the number of separate interpolations and transformations required.

    Parameters
    ----------
    points : npt.ArrayLike
        An array-like object containing the 3D points to be transformed, with shape (N, 3),
        where N is the number of points.
    timestamps : npt.ArrayLike
        An array-like object containing the timestamps corresponding to each point in the points
        array, with shape (N,).
    pose_path_adjustment : PosePath
        This PosePath is used to transform the points. Transforms are interpolated from supplied
        timestamps.
    resolution : float, optional, default: None
        The time resolution for grouping points. Points will be bucketed by this resolution and be
        adjusted based off of the average timestamp of the group. If not provided, will not group
        points and will interpolate each point using its timestamp
    extrapolation_strategy : str, optional, default: None
        Only supports "linear" extrapolation.

    Returns
    -------
    npt.NDArray
        A numpy array containing the transformed points, with shape (N, 3).
    """
    fill_value: FillValue = (
        "extrapolate" if extrapolation_strategy == "linear" else "nearest"
    )

    if resolution is None:
        return per_point_motion_compensation(
            points, timestamps, pose_path_adjustment, fill_value
        )
    else:
        return bucketed_motion_compensation(
            points, timestamps, pose_path_adjustment, fill_value, resolution
        )


def bucketed_motion_compensation(
    points: npt.ArrayLike,
    timestamps: npt.ArrayLike,
    pose_path_adjustment: PosePath,
    fill_value: FillValue = "nearest",
    resolution: Union[float, int] = 1000,
) -> npt.NDArray:
    """Computes motion compensation for points by bucketing them by timestamp
    and applying the same transformation to each point within the bucket.
    """
    points = np.asarray(points, dtype=np.float64).reshape((-1, 3))
    timestamps = np.asarray(timestamps).reshape((-1))

    # Create intervals and groups
    pd_timestamps = pd.Series(timestamps)
    intervals = (pd_timestamps / resolution).astype(int)
    groups = pd_timestamps.groupby(intervals)

    # Get groups timestamps and interpolate poses
    interval_timestamps = groups.mean()

    # Resample poses to generate the transforms
    transforms = pose_path_adjustment.interpolate(
        interval_timestamps, fill_value=fill_value
    ).as_matrix()

    # Prepare an empty array to store the transformed points
    # This is done to preserve order of points
    transformed_points = np.empty_like(points)

    for index, [_, group] in enumerate(groups):
        transformed_group = transform_points(transforms[index], points[group.index])
        transformed_points[group.index] = transformed_group

    return transformed_points


def per_point_motion_compensation(
    points: npt.ArrayLike,
    timestamps: npt.ArrayLike,
    pose_path_adjustment: PosePath,
    fill_value: FillValue = "nearest",
) -> npt.NDArray:
    """Applies per-point motion compensation to points."""
    transform_path = pose_path_adjustment.interpolate(timestamps, fill_value=fill_value)
    return apply_pose_path_to_points(transform_path, points)


def apply_pose_path_to_points(
    pose_path: PosePath, points: npt.ArrayLike
) -> npt.NDArray:
    """Transforms points using the poses of a pose path, matching pose_path[i] with points[i].

    Parameters
    ----------
    pose_path : PosePath
        The poses to use as transforms. Must be the same length as points.
    points : npt.ArrayLike
        An array-like object of points with shape (N, 3), where N must be the same as the number
        of poses.

    Returns
    -------
    npt.NDArray
        An array of transformed points with shape (N, 3).
    """
    points = np.asarray(points, dtype=np.float64).reshape((-1, 3))
    assert len(pose_path) == len(points), (
        "PosePath and points do not have the same length. "
        f"len(pose_path)={len(pose_path)} len(points)={len(points)}"
    )
    return np.array(
        [
            transform_points(t, [points[i]])[0]
            for i, t in enumerate(pose_path.as_matrix())
        ]
    )


def apply_pose_path_to_single_point(
    pose_path: PosePath, point: npt.ArrayLike
) -> npt.NDArray:
    """Transforms a single point using the poses of a pose path.

    Parameters
    ----------
    pose_path : PosePath
        The poses to use as transforms.
    point : npt.ArrayLike
        An array-like object of points with shape (N, 3), where N is the number of points.

    Returns
    -------
    npt.NDArray
        An array of transformed points with shape (N, 3), where N is the number of poses in
        pose_path.
    """
    points = np.asarray(point, dtype=np.float64).reshape((1, 3))
    return np.array([transform_points(t, points)[0] for t in pose_path.as_matrix()])
