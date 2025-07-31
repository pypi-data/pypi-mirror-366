"""Functions for working with Transform objects."""

from typing import Union
import numpy as np
import numpy.typing as npt
from scipy.spatial.transform import Rotation, Slerp

from scale_sensor_fusion_io import ITransformablePath, Pose


def interpolate_pose(a: Pose, b: Pose, factor: float) -> Pose:
    """Interpolate a Pose in between two other Poses.

    Parameters
    ----------
    a : Pose
        First Pose.
    b : Pose
        Second Pose.
    factor : float
        How close to b to interpolate in the range [0, 1]. Corresponds to the range [a, b].

    Returns
    -------
    Pose
        A Pose in between a and b.
    """
    assert 0.0 <= factor <= 1.0, f"factor {factor} is not in the range [0, 1]"

    slerp = Slerp(
        [0.0, 1.0],
        Rotation.concatenate([a.heading.as_rotation(), b.heading.as_rotation()]),
    )

    a_translation = np.asarray(a.position)
    b_translation = np.asarray(b.position)

    return Pose.from_rt(
        rotation=slerp([factor])[0],
        translation=a_translation + factor * (b_translation - a_translation),
    )


def transform_path(
    transform: Union[npt.NDArray, Pose], path: ITransformablePath
) -> ITransformablePath:
    """Apply a transformation to all poses in a ITransformablePath and return a new ITransformablePath.

    Parameters
    ----------
    transform : Union[npt.NDArray, Pose]
        Rotation and translation matrix.
    path : ITransformablePath
        Path to be transformed.

    Returns
    -------
    ITransformablePath
        Resulting path from transforming this object.
    """
    return type(path).from_matrix(transform @ path.as_matrix(), index=path.index)


def transform_points(
    transform: Union[npt.NDArray, Pose], points: npt.ArrayLike
) -> npt.NDArray[np.float64]:
    """Apply a rigid transformation to a list of points. Points should be (x, y, z).

    Parameters
    ----------
    transform : Union[npt.NDArray, Pose]
        Rotation and translation. Either a rigid transformation matrix or a Pose representing one.
    points : npt.ArrayLike
        Point cloud in the form [[x, y, z], ...].

    Returns
    -------
    npt.NDArray
        Transformed point cloud in the form [[x, y, z], ...].
    """
    if isinstance(transform, Pose):
        transform = transform.as_transform()
    return np.asarray(
        np.asarray(points, dtype=np.float64).reshape((-1, 3)) @ transform[:3, :3].T
        + transform[:3, 3]
    )


def transform_points_ignore_extra_data(
    transform: Union[npt.NDArray, Pose], points: npt.ArrayLike
) -> npt.NDArray[np.float64]:
    """Apply a rigid transformation to a list of points. Points should be at least length 3 in the
    form (x, y, z, ...). Anything past the first 3 elements is ignored (e.g. intensity, color).

    Parameters
    ----------
    transform : Union[npt.NDArray, Pose]
        Rotation and translation. Either a rigid transformation matrix or a Pose representing one.
    points : npt.ArrayLike
        Point cloud in the form [[x, y, z, ...], ...].

    Returns
    -------
    npt.NDArray
        Transformed point cloud in the form [[x, y, z, ...], ...].
    """
    points = np.asarray(points, dtype=np.float64)
    shape = points.shape if hasattr(points, 'shape') else None
    if not shape or len(shape) != 2 or shape[1] < 3:
        raise ValueError(f"invalid points shape {getattr(points, 'shape', None)}")

    if isinstance(transform, Pose):
        transform = transform.as_transform()

    points_4d = np.hstack([points[:, :3], np.ones((shape[0], 1))])
    transformed_4d = points_4d.dot(transform.T)
    return np.hstack([transformed_4d[:, :3], points[:, 3:]])
