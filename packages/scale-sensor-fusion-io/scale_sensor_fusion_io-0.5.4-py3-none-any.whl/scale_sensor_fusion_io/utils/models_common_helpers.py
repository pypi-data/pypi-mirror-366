"""Additional functionality for models.common"""
from typing import Iterable

import numpy as np
import numpy.typing as npt

from scale_sensor_fusion_io import Point3D


def point_3ds_to_matrix(points: Iterable[Point3D]) -> npt.NDArray[np.float64]:
    """Converts an iterable of Point3D objects into a matrix

    Parameters
    ----------
    points : Iterable[Point3D]
        Points to convert

    Returns
    -------
    npt.NDArray[np.float64]
        Matrix in the form [[x, y, z], ...] with the shape (len(points), 3)
    """
    return np.stack([np.asarray(point) for point in points])
