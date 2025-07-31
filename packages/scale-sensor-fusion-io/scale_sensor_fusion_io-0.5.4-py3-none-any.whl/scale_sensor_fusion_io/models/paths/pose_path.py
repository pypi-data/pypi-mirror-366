from __future__ import annotations

from functools import reduce
from typing import Iterator, Optional, Union

import numpy as np
import numpy.typing as npt
import pandas as pd
from numpy.typing import ArrayLike
from scipy.interpolate import make_interp_spline
from scipy.spatial.transform import Rotation

from .spacial_path import SpacialPath, SpacialInterpolationData

IDENTITY = (0, 0, 0, 0, 0, 0, 1)


class PosePath(SpacialPath):
    """PosePath class representing a list of poses at given timestamps, extending pandas DataFrame."""

    XYZ = ["x", "y", "z"]
    QUAT = ["qx", "qy", "qz", "qw"]
    COLUMNS = XYZ + QUAT

    def __init__(
        self, data: Union[ArrayLike, pd.DataFrame], index: Optional[ArrayLike] = None
    ):
        """Initializes the PosePath object.

        Args:
            data (Union[ArrayLike, pd.DataFrame]): An array or DataFrame of poses with shape (N, 7), where N is the number of poses.
            index (ArrayLike, optional): An array-like object representing the index (the timestamps) for the PosePath DataFrame. Defaults to None.
        """
        super().__init__(data=data, index=index, columns=PosePath.COLUMNS, dtype=float)

    def copy(self) -> PosePath:
        """Creates a copy of the current PosePath object.

        Returns:
            PosePath: A new PosePath object with copied data and index.
        """
        return PosePath(self.values.copy(), index=self.index)

    @classmethod
    def from_rt(
        cls,
        rotation: Rotation,
        translation: ArrayLike,
        index: Optional[ArrayLike] = None,
    ) -> PosePath:
        """Creates a PosePath object from rotations and translations.

        Args:
            rotation (Rotation): A Rotation object representing the rotations.
            translation (ArrayLike): An array-like object of translations with shape (N, 3), where N is the number of translations.
            index (ArrayLike, optional): An array-like object representing the index for the PosePath DataFrame. Defaults to None.

        Returns:
            PosePath: A PosePath object with the given rotation and translation.
        """
        positions = np.asarray(translation).reshape((-1, 3))
        headings = rotation.as_quat().reshape((-1, 4))
        assert len(headings) == len(positions)
        return PosePath(np.hstack([positions, headings]), index=index)

    @classmethod
    def from_csv(cls, file: str) -> PosePath:
        """Creates a PosePath object from a CSV file.

        Args:
            file (str): The path to the CSV file.

        Returns:
            PosePath: A PosePath object with data read from the CSV file.
        """
        return PosePath(pd.read_csv(file, index_col=0))

    @classmethod
    def identity(cls, n: int = 1, index: Optional[ArrayLike] = None) -> PosePath:
        """Create a PosePath object with identity poses.

        Args:
            n (int, optional): The number of identity poses. Defaults to 1.
            index (ArrayLike, optional): An array-like object representing the index for the PosePath DataFrame. Defaults to None.

        Returns:
            PosePath: A PosePath object with identity poses.
        """
        return PosePath(np.tile(IDENTITY, n).reshape((n, 7)), index=index)

    @classmethod
    def from_matrix(
        cls, matrix: ArrayLike, index: Optional[ArrayLike] = None
    ) -> PosePath:
        """Creates a PosePath object from transformation matrices.

        Args:
            matrix (ArrayLike): A 3D array-like object of transformation matrices with shape (N, 4, 4), where N is the number of matrices.
            index (ArrayLike, optional): An array-like object representing the index for the PosePath DataFrame. Defaults to None.

        Returns:
            PosePath: A PosePath object with poses represented by the given transformation matrices.
        """
        matrix = np.asarray(matrix).reshape((-1, 4, 4))
        return PosePath.from_rt(
            Rotation.from_matrix(matrix[:, :3, :3]), matrix[:, :3, 3], index=index
        )

    def as_matrix(self) -> npt.NDArray:
        """Convert the PosePath object to transformation matrices.

        Returns:
            npt.NDArray: A 3D array of transformation matrices with shape (N, 4, 4), where N is the number of poses.
        """
        matrix = np.tile(np.eye(4), (len(self), 1, 1))
        matrix[:, :3, :3] = Rotation.from_quat(self.headings).as_matrix()
        matrix[:, :3, 3] = self.positions
        return matrix

    @classmethod
    def from_euler(cls, seq: str, angles: ArrayLike, degrees: bool = False) -> PosePath:
        """Creates a PosePath object from Euler angles.

        Args:
            seq (str): The Euler sequence of axes, such as 'xyz', 'zyx', etc.
            angles (ArrayLike): An array-like object of Euler angles with shape (N, len(seq)), where N is the number of poses.
            degrees (bool, optional): If True, angles are in degrees. Defaults to False.

        Returns:
            PosePath: A PosePath object with poses represented by the given Euler angles.
        """
        angles = np.asarray(angles).reshape((-1, len(seq)))
        path = PosePath.identity(n=len(angles))
        path.headings = Rotation.from_euler(seq, angles, degrees).as_quat()
        return path

    def as_euler(self, seq: str, degrees: bool = False) -> npt.NDArray:
        """Converts the PosePath object to Euler angles.

        Args:
            seq (str): The Euler sequence of axes, such as 'xyz', 'zyx', etc.
            degrees (bool, optional): If True, angles are in degrees. Defaults to False.

        Returns:
            np.ndarray: An array of Euler angles with shape (N, len(seq)), where N is the number of poses.
        """
        return Rotation.from_quat(self.headings).as_euler(seq, degrees=degrees)

    @classmethod
    def from_positions(cls, positions: ArrayLike) -> PosePath:
        """Creates a PosePath object with given positions.

        Args:
            positions (ArrayLike): An array-like object of positions with shape (N, 3), where N is the number of positions.

        Returns:
            PosePath: A PosePath object with poses represented by the given positions and identity orientations.
        """
        positions = np.asarray(positions).reshape((-1, 3))
        path = PosePath.identity(len(positions))
        path.positions = positions
        return path

    @property
    def positions(self) -> npt.NDArray:
        """Gets the positions of the poses.

        Returns:
            npt.NDArray: An array of positions with shape (N, 3), where N is the number of poses.
        """
        return self.values[:, 0:3]

    @positions.setter
    def positions(self, values: ArrayLike) -> None:
        """Set the positions of the poses.

        Args:
            values (ArrayLike): Anarray-like object of positions with shape (N, 3), where N is the number of positions.
        """
        self.values[:, 0:3] = np.asarray(values).reshape((-1, 3))

    @property
    def headings(self) -> npt.NDArray:
        """Gets the orientations (headings) of the poses in quaternions.

        Returns:
            npt.NDArray: An array of quaternions with shape (N, 4), where N is the number of poses.
        """
        return self.values[:, 3:7]

    @headings.setter
    def headings(self, values: ArrayLike) -> None:
        """Sets the orientations (headings) of the poses in quaternions.

        Args:
            values (ArrayLike): An array-like object of quaternions with shape (N, 4), where N is the number of orientations.
        """
        self.values[:, 3:7] = np.asarray(values).reshape((-1, 4))

    # Operations
    def invert(self) -> PosePath:
        """Creates a new PosePath instance with inverted poses.

        Returns:
            PosePath: A PosePath object with inverted poses.
        """
        inv_rotations = Rotation.from_quat(self.headings).inv()
        inv_positions = -inv_rotations.apply(self.positions)
        return PosePath.from_rt(inv_rotations, inv_positions, index=self.index)

    def __matmul__(self, other: Union[PosePath, ArrayLike]) -> PosePath:
        """Matrix multiplication of the PosePath object with another PosePath object or a transformation matrix.

        Args:
            other (Union['PosePath', ArrayLike]): Another PosePath object or a transformation matrix/array.

        Returns:
            PosePath: A PosePath object with poses resulting from the matrix multiplication.
        """
        if isinstance(other, PosePath):
            resampled = other.interpolate(self.index)
            return PosePath.from_matrix(
                self.as_matrix() @ resampled.as_matrix(), index=self.index
            )

        return PosePath.from_matrix(
            self.as_matrix() @ np.asarray(other), index=self.index
        )

    def __rmatmul__(self, other: Union[PosePath, ArrayLike]) -> PosePath:
        """Right matrix multiplication of the PosePath object with another PosePath object or a transformation matrix.

        Args:
            other (Union['PosePath', ArrayLike]): Another PosePath object or a transformation matrix/array.

        Returns:
            PosePath: A PosePath object with poses resulting from the matrix multiplication.
        """
        if isinstance(other, PosePath):
            resampled = other.interpolate(self.index)
            return PosePath.from_matrix(
                resampled.as_matrix() @ self.as_matrix(), index=self.index
            )

        return PosePath.from_matrix(
            np.asarray(other) @ self.as_matrix(), index=self.index
        )

    @classmethod
    def multiply(cls, paths: Iterator[PosePath]) -> PosePath:
        """Composes multiple PosePath objects.

        Args:
            paths (Iterator['PosePath']): An iterator of PosePath objects.

        Returns:
            PosePath: A PosePath object with poses resulting from the matrix multiplication of the given PosePath objects.
        """
        return reduce(cls.__rmatmul__, paths)

    def make_relative(self) -> PosePath:
        """Creates a new PosePath object with poses relative to the first pose.

        Returns:
            PosePath: A new PosePath object with poses relative to the first pose in the original PosePath object.
        """
        inv_first = self[:1].invert().as_matrix()[0]
        return inv_first @ self

    def __getitem__(self, key):
        result = super().__getitem__(key)
        if isinstance(result, pd.Series):
            return result
        elif isinstance(result, pd.DataFrame) and np.array_equal(
            result.columns, PosePath.COLUMNS
        ):
            return PosePath(result)
        return result

    # InterpolateablePath
    @classmethod
    def from_interpolation_data(
        cls, value: SpacialInterpolationData, index: npt.NDArray
    ) -> PosePath:
        """Creates a PosePath from interpolated values

        Parameters
        ----------
        values : SpacialInterpolationData
            Interpolated position and rotation
        index : npt.NDArray
            Timestamps

        Returns
        -------
        PosePath
            Result of interpolation.
        """
        assert (
            value.spherical is not None and value.linear is not None
        ), f"Unexpected None value in data {value}"
        return PosePath.from_rt(value.spherical, value.linear, index=index)

    def get_interpolation_data(self) -> SpacialInterpolationData:
        """Gets the values of this object for interpolation.

        Returns
        -------
        SpacialInterpolationData
            Position and rotation.
        """
        return SpacialInterpolationData(
            linear=self.positions, spherical=Rotation.from_quat(self.headings)
        )

    def calculate_kinematics(self, time_unit_to_second_conversion: int = 1e9) -> pd.DataFrame:
        """Calculate the velocity and acceleration vectors of the pose path by
            fitting a spline to the positions and computing 1st and 2nd
            derivatives for each dimension. Also converts the timestamps to
            seconds (assumes nanoseconds by default).

        Returns:
            pd.DataFrame: A pandas DataFrame with the xyz components of the
                            velocity and acceleration of the pose path at each
                            timestamp with columns [vx, vy, vz, ax, ay, az].
        """
        timestamps_in_seconds = self.index / time_unit_to_second_conversion

        def calculate_1d_kinematics(axis: int) -> (npt.NDArray, npt.NDArray):
            spline = make_interp_spline(timestamps_in_seconds, self.positions[:, axis])
            velocities = spline(timestamps_in_seconds, nu=1)
            accelerations = spline(timestamps_in_seconds, nu=2)
            return velocities, accelerations

        x_velocities, x_accelerations = calculate_1d_kinematics(0)
        y_velocities, y_accelerations = calculate_1d_kinematics(1)
        z_velocities, z_accelerations = calculate_1d_kinematics(2)

        return pd.DataFrame({
            'vx': x_velocities,
            'vy': y_velocities,
            'vz': z_velocities,
            'ax': x_accelerations,
            'ay': y_accelerations,
            'az': z_accelerations
        }, index=timestamps_in_seconds)
