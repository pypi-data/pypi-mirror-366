"""Pose class definition."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Collection, Optional, Type, Union

import numpy as np
import numpy.typing as npt
from scipy.spatial.transform import Rotation

from .common import Point3D, QuaternionData


@dataclass
class Pose:
    """A data class representing a pose in a 3D space. The pose includes both position and
    orientation.

    Attributes
    ----------
    heading : QuaternionData
        Orientation in the 3D space.
    position : Point3D
        Position in 3D space.
    """

    heading: QuaternionData
    position: Point3D

    def copy(self) -> Pose:
        """Creates a copy of this object.

        Returns
        -------
        Pose
            Clone of this object.
        """
        return Pose(heading=self.heading.copy(), position=self.position.copy())

    def as_euler(self, seq: str = "XYZ", degrees: bool = False) -> npt.NDArray:
        """Gets this object's heading as Euler angles.

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
        return self.heading.as_euler(seq=seq, degrees=degrees)

    @staticmethod
    def from_euler(
        angles: npt.ArrayLike,
        seq: str = "XYZ",
        degrees: bool = False,
    ) -> Pose:
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
            Rotation as a Quaternion.
        """
        return Pose(
            heading=QuaternionData.from_euler(angles, seq=seq, degrees=degrees),
            position=Point3D.identity(),
        )

    @staticmethod
    def identity() -> Pose:
        """Represents no transformation

        Returns
        -------
        Pose:
            Identity rotation and translation pose.
        """
        return Pose(heading=QuaternionData.identity(), position=Point3D.identity())

    @staticmethod
    def from_rt(
        rotation: Optional[Union[QuaternionData, Rotation]] = None,
        translation: Optional[Union[Collection[float], Point3D]] = None,
    ) -> Pose:
        """Creates a Pose from a Rotation and a translation vector.

        Parameters
        ----------
        rotation : Union[Quaternion, QuaternionData, Rotation], optional
            A scipy Rotation object, by default None
        translation : Collection[float], optional
            Translation vector (x, y, z), by default None

        Returns
        -------
        Pose
            Object with rotation and translation aspects.
        """
        if rotation is None:
            rotation = QuaternionData.identity()
        elif isinstance(rotation, Rotation):
            rotation = QuaternionData.from_rotation(rotation)
        else:
            rotation = rotation.copy()

        if translation is None:
            translation = Point3D.identity()
        elif isinstance(translation, Point3D):
            translation = translation.copy()
        else:
            translation = Point3D(*translation)

        return Pose(
            position=translation,
            heading=rotation,
        )

    def as_transform(self) -> npt.NDArray[np.float64]:
        """Creates a rigid transformation matrix from a Pose.

        Returns
        -------
        npt.NDArray[np.float64]:
            A 4x4 matrix representing the rigid transformation matrix.
            ```py
            [
                [ r00, r01, r02, t0],
                [ r10, r11, r12, t1],
                [ r20, r21, r22, t2],
                [ 0, 0, 0, 1]
            ]
            ```
        """
        return np.block(
            [
                [
                    self.heading.as_matrix(),
                    np.asarray(self.position).reshape((3, 1)),
                ],
                [np.zeros(3), 1],
            ]
        )

    @staticmethod
    def from_transform(transform_matrix: npt.ArrayLike) -> Pose:
        """
        Creates a Pose from a rigid transformation matrix.

        Parameters
        ----------
        transform_matrix : npt.ArrayLike
            An object representing the rigid transformation matrix. Also accepts a 3x3 rotation
            matrix or a length 3 translation vector.
            ```py
            [
                [ r00, r01, r02, t0],
                [ r10, r11, r12, t1],
                [ r20, r21, r22, t2],
                [ 0, 0, 0, 1]
            ]
            ```

        Returns
        -------
        Pose
            A Pose object corresponding to the provided rigid transformation matrix.
        """
        transform_matrix = np.asarray(transform_matrix, dtype=np.float64)
        num_elements = np.prod(transform_matrix.shape)
        if num_elements == 16:
            transform_matrix = transform_matrix.reshape((4, 4))
            return Pose(
                heading=QuaternionData.from_matrix(transform_matrix[:3, :3]),
                position=Point3D(*transform_matrix[:3, 3]),
            )
        elif num_elements == 9:
            return Pose(
                heading=QuaternionData.from_matrix(transform_matrix),
                position=Point3D.identity(),
            )
        elif num_elements == 3:
            return Pose(
                heading=QuaternionData.identity(),
                position=Point3D(*transform_matrix.flatten()),
            )
        else:
            raise ValueError(f"Invalid shape {transform_matrix.shape}")

    @staticmethod
    def from_transformed_points(a: npt.ArrayLike, b: npt.ArrayLike) -> Pose:
        """Create a transform roughly mapping two point clouds together.
        Point clouds must have the same number of points
        and the point a[i] must correspond to point b[i].

        Parameters
        ----------
        a : npt.ArrayLike
            [[x, y, z], ...] Point cloud A
        b : npt.ArrayLike
            [[x, y, z], ...] Point cloud B

        Returns
        -------
        Pose
            The pose such that transform_points(pose, a) -> b
        """
        a = np.asarray(a, dtype=np.float64).reshape((-1, 3))
        b = np.asarray(b, dtype=np.float64).reshape((-1, 3))
        assert (
            tuple(a.shape) == tuple(b.shape)
        ), f"Point clouds do not have the same shape a={a.shape} b={b.shape}"

        centroid_a = np.mean(a, axis=0)
        centroid_b = np.mean(b, axis=0)
        relative_a = a - centroid_a
        relative_b = b - centroid_b

        c = relative_a.T @ relative_b
        v, s, w = np.linalg.svd(c)

        if (np.linalg.det(v) * np.linalg.det(w)) < 0.0:
            s[-1] = -s[-1]
            v[:, -1] = -v[:, -1]

        rotation = v @ w
        translation = centroid_b - centroid_a @ rotation

        return Pose.from_rt(Rotation.from_matrix(rotation.T), translation)

    @property
    def inverse(self) -> Pose:
        """Inverse of this object. When transforming points, the inverse will be the transformation
        in the opposite direction.

        Returns
        -------
        Pose
            Inverse of this object.
        """
        inverse_rotation = self.heading.as_rotation().inv()
        return Pose.from_rt(
            inverse_rotation, np.dot(-inverse_rotation.as_matrix(), self.position)
        )

    def __array__(
        self, dtype: Optional[Union[np.dtype, str, Type]] = None
    ) -> npt.NDArray:
        return np.array(
            [
                self.position.x,
                self.position.y,
                self.position.z,
                self.heading.x,
                self.heading.y,
                self.heading.z,
                self.heading.w,
            ],
            dtype=dtype,
        )

    def __eq__(self, other: Any) -> bool:
        if (
            hasattr(other, "heading")
            and hasattr(other, "position")
            and self.heading == other.heading
            and self.position == other.position
        ):
            return True
        us = self.__array__()
        other = np.asarray(other)
        return np.prod(us.shape) == np.prod(other.shape) and np.allclose(
            us, other.reshape(us.shape)
        )

    def __matmul__(self, other: Any) -> Any:
        if isinstance(other, Pose):
            return Pose.from_transform(self.as_transform() @ other.as_transform())
        return self.as_transform() @ other

    def __imatmul__(self, other: Any) -> Any:
        if isinstance(other, Pose):
            other = other.as_transform()
        result = Pose.from_transform(self.as_transform() @ other)
        self.heading = result.heading
        self.position = result.position
        return self

    def __repr__(self) -> str:
        return f"heading={self.heading} position={self.position}"
