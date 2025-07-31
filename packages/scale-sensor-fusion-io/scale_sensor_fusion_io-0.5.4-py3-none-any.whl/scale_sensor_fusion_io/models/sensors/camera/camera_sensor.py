import os
from dataclasses import dataclass
from typing import List, Literal, Optional, Tuple
import tempfile

import numpy as np
import numpy.typing as npt
from scale_sensor_fusion_io.models.sensors.camera import (
    CameraIntrinsics,
)
from scale_sensor_fusion_io.utils.video_helpers import VideoReader

from ...common import SensorID, SensorKind
from ...paths import PosePath


@dataclass
class CameraSensorVideo:
    timestamps: List[int]
    content: npt.NDArray[np.uint8]
    fps: float


@dataclass
class CameraSensorImage:
    timestamp: int
    content: npt.NDArray[np.uint8]


@dataclass
class CameraSensor:
    id: SensorID
    poses: PosePath
    intrinsics: CameraIntrinsics
    video: Optional[CameraSensorVideo] = None
    images: Optional[List[CameraSensorImage]] = None
    type: Literal[SensorKind.Camera] = SensorKind.Camera
    parent_id: Optional[SensorID] = None
    coordinates: Literal["ego", "world"] = "world"

    video_loader: Optional[VideoReader] = None

    def __init__(
        self,
        id: SensorID,
        poses: PosePath,
        intrinsics: CameraIntrinsics,
        video: Optional[CameraSensorVideo] = None,
        images: Optional[List[CameraSensorImage]] = None,
        type: Literal[SensorKind.Camera] = SensorKind.Camera,
        parent_id: Optional[SensorID] = None,
    ) -> None:
        self.id = id
        self.poses = poses
        self.intrinsics = intrinsics
        self.video = video
        self.images = images
        self.type = type
        self.parent_id = parent_id

        if video is not None:
            self.video_loader: Optional[VideoReader] = VideoReader(
                video=video.content.tobytes()
            )

    def get_closest_content_at_timestamp(
        self, timestamp: int
    ) -> Tuple[npt.NDArray[np.uint8], int]:
        content_timestamps: List[int]
        if self.video:
            content_timestamps = self.video.timestamps
        elif self.images:
            content_timestamps = [image.timestamp for image in self.images]
        else:
            raise Exception("Missing camera content")

        # Find the closest timestamp to the provided timestamp
        closest_frame = int(np.argmin(np.abs(np.array(content_timestamps) - timestamp)))

        return (
            self.get_content_at_frame(closest_frame),
            content_timestamps[closest_frame],
        )

    def get_content_at_frame(self, frame: int) -> npt.NDArray[np.uint8]:
        if self.video:
            if not self.video_loader:
                self.video_loader: Optional[VideoReader] = VideoReader(
                    video=self.video.content.tobytes()
                )
                if not self.video_loader:
                    raise Exception("Missing video loader")
            return self.video_loader.load(frame)
        elif self.images:
            return self.images[frame].content
        else:
            raise Exception("Missing camera content")
