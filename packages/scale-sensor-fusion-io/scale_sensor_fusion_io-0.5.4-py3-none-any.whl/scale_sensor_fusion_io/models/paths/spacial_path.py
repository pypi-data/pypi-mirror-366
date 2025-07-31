"""Contains InterpolateablePath ABC"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

import numpy as np
import numpy.typing as npt
import pandas as pd
from scipy.interpolate import interp1d
from scipy.spatial.transform import Rotation, Slerp


from ..common import FillValue


@dataclass
class SpacialInterpolationData:
    """Values to use for interpolation

    Members
    -------
    linear : Optional[npt.NDArray], optional, default: None
    spherical : Optional[Rotation], optional, default: None
    """

    linear: Optional[npt.NDArray] = None
    spherical: Optional[Rotation] = None

    def __repr__(self) -> str:
        return f"(linear={self.linear} spherical={self.spherical})"


class SpacialPath(ABC, pd.DataFrame):
    """A path containing 3D spacial data."""

    @staticmethod
    def __lerp(
        x: npt.NDArray,
        y: Optional[npt.NDArray],
        t: npt.NDArray,
        x_sorted_order: Optional[npt.NDArray[np.int32]],
        t_sorted_order: Optional[npt.NDArray[np.int32]],
        t_unsorted_order: Optional[npt.NDArray[np.int32]],
        fill_value: FillValue,
    ) -> Optional[npt.NDArray]:
        """Helper function for SpacialPath.interpolate. Handles linear interpolation."""
        if y is None:
            return None

        if x_sorted_order is not None:
            y = y[x_sorted_order]

        if t_sorted_order is not None:
            t = t[t_sorted_order]

        if fill_value == "nearest":
            interpolator_fill_value = (y[0], y[-1])
        elif fill_value == "identity":
            interpolator_fill_value = np.zeros(6)
        else:
            interpolator_fill_value = fill_value

        lerp = interp1d(
            x=x, y=y, bounds_error=False, fill_value=interpolator_fill_value, axis=0  # type: ignore
        )
        result = lerp(t)

        if t_unsorted_order is not None:
            result = result[t_unsorted_order]
        return result

    @staticmethod
    def __slerp(
        x: npt.NDArray,
        y: Optional[Rotation],
        t: npt.NDArray,
        x_sorted_order: Optional[npt.NDArray[np.int32]],
        t_sorted_order: Optional[npt.NDArray[np.int32]],
        t_unsorted_order: Optional[npt.NDArray[np.int32]],
        fill_value: FillValue,
    ) -> Optional[Rotation]:
        """Helper function for SpacialPath.interpolate. Handles spherical linear interpolation."""
        if y is None or len(x) == 0:
            return None

        if x_sorted_order is not None:
            y = y[x_sorted_order]

        if t_sorted_order is not None:
            t = t[t_sorted_order]

        lower_bound = np.searchsorted(t, x[0], side="left")
        upper_bound = np.searchsorted(t, x[-1], side="right")

        slerp = Slerp(x, y)
        rotations = []
        if lower_bound > 0:
            angles = SpacialPath.__lerp(
                x, y.as_euler("xyz"), t[:lower_bound], None, None, None, fill_value
            )
            if angles is not None:
                rotations.append(
                    Rotation.from_euler(
                        "xyz",
                        angles,
                    )
                )

        if lower_bound < upper_bound:
            rotations.append(slerp(t[lower_bound:upper_bound]))

        if upper_bound < len(t):
            angles = SpacialPath.__lerp(
                x, y.as_euler("xyz"), t[upper_bound:], None, None, None, fill_value
            )
            if angles is not None:
                rotations.append(
                    Rotation.from_euler(
                        "xyz",
                        angles,
                    )
                )

        result = Rotation.concatenate(rotations)

        if t_unsorted_order is not None and result is not None:
            result = result[t_unsorted_order]
        return result

    def interpolate(
        self: SpacialPathT,
        index: npt.ArrayLike,
        fill_value: FillValue = "nearest",
    ) -> SpacialPathT:
        """Interpolate a 3D path object at the given indices.

        Parameters
        ----------
        path : SpacialPathT
            3D spacial data (rotation + translation) over time.
        index : npt.ArrayLike
            Timestamps to interpolate the path at.
        fill_value : FillValue, optional, default: "nearest"
            How to handle out of bound data.

        Returns
        -------
        SpacialPathT
            A path object with values interpolated at the given indices.
        """
        index = np.asarray(index).flatten()
        if np.array_equal(self.index, index):
            return self.copy()

        if len(self.index) == 0:
            raise ValueError("Cannot interpolate with empty path")
        if len(self.index) == 1:
            return type(self)(self.take([0] * len(index)).values, index=index)

        # index and path.index need to be sorted
        if np.any(index[1:] < index[:-1]):
            input_sorted_order = np.argsort(index)
            input_unsorted_order = np.argsort(input_sorted_order)
        else:
            input_sorted_order = None
            input_unsorted_order = None

        x = self.index.to_numpy().flatten()
        y = self.get_interpolation_data()
        if np.any(x[1:] < x[:-1]):
            x_sorted_order = np.argsort(x)
            x = x[x_sorted_order]
        else:
            x_sorted_order = None

        values = SpacialInterpolationData(
            linear=SpacialPath.__lerp(
                x,
                y.linear,
                index,
                x_sorted_order,
                input_sorted_order,
                input_unsorted_order,
                fill_value,
            ),
            spherical=SpacialPath.__slerp(
                x,
                y.spherical,
                index,
                x_sorted_order,
                input_sorted_order,
                input_unsorted_order,
                fill_value,
            ),
        )

        return type(self).from_interpolation_data(values, index=index)

    @classmethod
    @abstractmethod
    def from_interpolation_data(
        cls: Type[SpacialPathT],
        value: SpacialInterpolationData,
        index: npt.NDArray,
    ) -> SpacialPathT:
        ...

    @abstractmethod
    def get_interpolation_data(self) -> SpacialInterpolationData:
        ...


SpacialPathT = TypeVar("SpacialPathT", bound=SpacialPath)
