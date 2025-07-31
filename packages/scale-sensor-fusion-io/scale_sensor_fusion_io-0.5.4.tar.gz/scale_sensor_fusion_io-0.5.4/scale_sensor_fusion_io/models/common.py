"""Models shared across other models."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal, Optional, Type, Union

import numpy as np
import numpy.typing as npt
from scipy.spatial.transform import Rotation

AnnotationID = Union[str, int]
FillValue = Union[Literal["nearest"], Literal["identity"], Literal["extrapolate"]]
SensorID = Union[str, int]


class AnnotationKind(Enum):
    Attributes = "attributes"
    Box2D = "box_2d"
    Cuboid = "cuboid"
    Event = "event"
    LabeledPoints = "labeled_points"
    PointSegmentation = "point_segmentation"
    LocalizationAdjustment = "localization_adjustment"
    Object = "object"
    Polygon = "polygon"
    PolygonTopdown = "polygon_topdown"
    Polyline = "polyline"
@dataclass
class Point3D:
    """A point in 3D space."""

    x: float
    y: float
    z: float

    def copy(self) -> Point3D:
        """Creates a copy of this object.

        Returns
        -------
        Point3D
            A clone of this object.
        """
        return Point3D(x=self.x, y=self.y, z=self.z)

    @staticmethod
    def identity() -> Point3D:
        """Represents no translation.

        Returns
        -------
        Point3D
            (0, 0, 0)
        """
        return Point3D(x=0.0, y=0.0, z=0.0)

    def __array__(
        self, dtype: Optional[Union[np.dtype, str, Type]] = None
    ) -> npt.NDArray[np.float64]:
        return np.array([self.x, self.y, self.z], dtype=dtype)

    def __eq__(self, other: Any) -> bool:
        if (
            hasattr(other, "x")
            and hasattr(other, "y")
            and hasattr(other, "z")
            and self.x == other.x
            and self.y == other.y
            and self.z == other.z
        ):
            return True
        us = self.__array__()
        other = np.asarray(other)
        return np.prod(us.shape) == np.prod(other.shape) and np.allclose(
            us, other.reshape(us.shape)
        )

    def __repr__(self) -> str:
        return f"(x={float(self.x):.3} y={float(self.y):.3} z={float(self.z):.3})"


@dataclass
class QuaternionData:
    """A Quaternion representing rotation in 3D space."""

    x: float
    y: float
    z: float
    w: float

    def copy(self) -> QuaternionData:
        """Creates a copy of this object.

        Returns
        -------
        QuaternionData
            Clone of this object.
        """
        return QuaternionData(x=self.x, y=self.y, z=self.z, w=self.w)

    def as_euler(
        self, seq: str = "XYZ", degrees: bool = False
    ) -> npt.NDArray[np.float64]:
        """Get this object as Euler angles.

        Parameters
        ----------
        seq : str, optional
            3 characters belonging to the set {'X', 'Y', 'Z'} for intrinsic rotations,
            or {'x', 'y', 'z'} for extrinsic rotations [1]. Adjacent axes cannot be the same.
            Extrinsic and intrinsic rotations cannot be mixed in one function call.
            By default "XYZ"
        degrees : bool, optional
            Whether angles are in degrees, by default False

        Returns
        -------
        npt.NDArray
            Vector of Euler angles.
        """
        return np.asarray(self.as_rotation().as_euler(seq, degrees=degrees))

    @staticmethod
    def from_euler(
        angles: npt.ArrayLike,
        seq: str = "XYZ",
        degrees: bool = False,
    ) -> QuaternionData:
        """Create a transform from Euler angles.

        Parameters
        ----------
        angles : ArrayLike[float]
            Euler angles
        seq : str, optional
            3 characters belonging to the set {'X', 'Y', 'Z'} for intrinsic rotations,
            or {'x', 'y', 'z'} for extrinsic rotations [1]. Adjacent axes cannot be the same.
            Extrinsic and intrinsic rotations cannot be mixed in one function call.
            By default "XYZ"
        degrees : bool, optional
            Whether angles are in degrees, by default False

        Returns
        -------
        QuaternionData:
            The angles as a Quaternion.
        """
        return QuaternionData(*Rotation.from_euler(seq, angles, degrees).as_quat())

    def as_matrix(self) -> npt.NDArray[np.float64]:
        """Creates a rotation matrix.

        Returns
        -------
        npt.NDArray[np.float64]:
            A 3x3 rotation matrix.
            ```py
            [
                [ r00, r01, r02],
                [ r10, r11, r12],
                [ r20, r21, r22],
            ]
            ```
        """
        return np.asarray(Rotation.from_quat(self).as_matrix(), dtype=np.float64)

    @staticmethod
    def from_matrix(rotation_matrix: npt.ArrayLike) -> QuaternionData:
        """
        Creates a QuaternionData object from a rotation matrix.

        Parameters
        ----------
        rotation_matrix : npt.ArrayLike
            An object representing a 3x3 rotation matrix.
            ```py
            [
                [ r00, r01, r02],
                [ r10, r11, r12],
                [ r20, r21, r22],
            ]
            ```

        Returns
        -------
        QuaternionData
            A QuaternionData object corresponding to the provided rotation.
        """
        return QuaternionData(
            *Rotation.from_matrix(
                np.asarray(rotation_matrix, dtype=np.float64).reshape((3, 3))
            ).as_quat()
        )

    def as_rotation(self) -> Rotation:
        """Gets this object as a scipy Rotation object.

        Returns
        -------
        Rotation
            Equivalent Rotation object.
        """
        return Rotation.from_quat(self)

    @staticmethod
    def from_rotation(rotation: Rotation) -> QuaternionData:
        """Creates a QuaternionData object from scipy Rotation.

        Parameters
        ----------
        rotation : Rotation
            The rotation to copy.

        Returns
        -------
        QuaternionData
            Equivalent QuaternionData object.
        """
        return QuaternionData(*rotation.as_quat())

    @staticmethod
    def identity() -> QuaternionData:
        """Represents no rotation.

        Returns
        -------
        QuaternionData
            (x=0, y=0, z=0, w=1)
        """
        return QuaternionData(x=0.0, y=0.0, z=0.0, w=1.0)

    def __array__(
        self, dtype: Optional[Union[np.dtype, str, Type]] = None
    ) -> npt.NDArray[np.float64]:
        return np.array([self.x, self.y, self.z, self.w], dtype=dtype)

    def __eq__(self, other: Any) -> bool:
        if (
            hasattr(other, "x")
            and hasattr(other, "y")
            and hasattr(other, "z")
            and hasattr(other, "w")
            and self.x == other.x
            and self.y == other.y
            and self.z == other.z
            and self.w == other.w
        ):
            return True
        us = self.__array__()
        other = np.asarray(other)
        return np.prod(us.shape) == np.prod(other.shape) and np.allclose(
            us, other.reshape(us.shape)
        )

    def __repr__(self) -> str:
        return f"(x={float(self.x):.3} y={float(self.y):.3} z={float(self.z):.3} w={float(self.w):.3})"


class SensorKind(Enum):
    Camera = "camera"
    Lidar = "lidar"
    Radar = "radar"
    Points = "points"
    Odometer = "odometer"
