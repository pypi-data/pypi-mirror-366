"""Contains ITransformablePath"""
from __future__ import annotations
from typing_extensions import Protocol

import numpy as np
import numpy.typing as npt
import pandas as pd


class ITransformablePath(Protocol):
    """A path that can be transformed using Pose or rigid transformation matrices."""

    @property
    def index(self) -> pd.Index:
        ...

    def as_matrix(self) -> npt.NDArray[np.float64]:
        ...

    @staticmethod
    def from_matrix(matrix: npt.ArrayLike, index: npt.ArrayLike) -> ITransformablePath:
        ...
