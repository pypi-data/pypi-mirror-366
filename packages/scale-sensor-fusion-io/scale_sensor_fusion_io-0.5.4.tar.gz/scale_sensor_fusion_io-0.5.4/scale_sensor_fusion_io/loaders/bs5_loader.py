from enum import Enum
from typing import Optional, cast

import dacite
from scale_json_binary import JSONBinaryEncoder

from ..spec import BS5

encoder = JSONBinaryEncoder()


def _fix_data_shape(scene: BS5.Scene) -> BS5.Scene:
    """
    When reading via dacite, the numpy arrays aren't correctly shaped (since that's not included in the typedef)
    This function fixes all the fields that need to be reshaped
    """
    if scene.sensors:
        for sensor in scene.sensors:
            if sensor.type == "lidar":
                for l_frame in sensor.frames:
                    l_frame.points.positions = l_frame.points.positions.reshape(-1, 3)
                    if l_frame.points.colors is not None:
                        l_frame.points.colors = l_frame.points.colors.reshape(-1, 3)

            elif sensor.type == "radar":
                for r_frame in sensor.frames:
                    r_frame.points.positions = r_frame.points.positions.reshape(-1, 3)
                    if r_frame.points.directions is not None:
                        r_frame.points.directions = r_frame.points.directions.reshape(
                            -1, 3
                        )
                    if r_frame.points.lengths is not None:
                        r_frame.points.lengths = r_frame.points.lengths.reshape(-1, 3)

            elif sensor.type == "points":
                sensor.points.positions = sensor.points.positions.reshape(-1, 3)
    return scene


class BS5Loader:
    def __init__(
        self,
        scene_url: str,
    ):
        self.scene_url = scene_url

    def load(self) -> BS5.Scene:
        raw_data: bytes
        with open(self.scene_url, "rb") as fd:
            raw_data = cast(bytes, fd.read())
        return self.load_from_bytes(raw_data)
        

    @staticmethod
    def load_from_bytes(raw_data: bytes) -> BS5.Scene:
        obj = encoder.loads(raw_data)
        if "version" not in obj or not obj["version"].startswith("5.1") and not obj["version"].startswith("1.0"):
            raise Exception(f"Cannot load scene with version {obj['version']}")

        scene_bs5 = dacite.from_dict(
            data_class=BS5.Scene,
            data=obj,
            config=dacite.Config(
                cast=[Enum, tuple],
            ),
        )

        scene = _fix_data_shape(scene_bs5)

        return scene

    def load_as_bs5(self) -> BS5.Scene:
        raw_data: bytes
        with open(self.scene_url, "rb") as fd:
            raw_data = cast(bytes, fd.read())

        obj = encoder.loads(raw_data)
        if "version" not in obj or not obj["version"].startswith("5."):
            raise Exception(f"Cannot load scene with version {obj['version']}")

        scene_bs5 = dacite.from_dict(
            data_class=BS5.Scene,
            data=obj,
            config=dacite.Config(cast=[Enum, tuple]),
        )

        return scene_bs5
