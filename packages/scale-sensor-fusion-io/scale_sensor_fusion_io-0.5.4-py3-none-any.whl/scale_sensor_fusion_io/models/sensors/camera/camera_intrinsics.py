from dataclasses import dataclass
from typing import Optional

from . import CameraDistortion


@dataclass
class CameraIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    width: int
    height: int

    distortion: Optional[CameraDistortion]
    skew: float = 0
    scale_factor: float = 0
