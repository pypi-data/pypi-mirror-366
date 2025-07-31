from typing import Sequence, Optional, Tuple

import numpy as np
import numpy.typing as npt
from scale_sensor_fusion_io.models.sensors.camera.camera_sensor import CameraSensor
from scale_sensor_fusion_io.utils.camera_helpers import global_to_local, project_distort


def compute_photocolors(
    positions: npt.NDArray[np.float32],
    cameras: Sequence[CameraSensor],
    points_timestamps: Optional[npt.NDArray[np.uint32]],
    frame_timestamp: Optional[int],
) -> npt.NDArray[np.uint8]:
    """
    Compute photocolors for provided points.

    Photocolors are computed by projecting each point into each camera and
    sampling the color of the pixel that the point projects to.
    """
    # initialize color to shape of point position
    colors = np.full(positions.shape, 255, dtype=np.uint8)

    start_timestamp = (
        int(np.min(points_timestamps))
        if points_timestamps is not None
        else frame_timestamp
    )
    if start_timestamp is None:
        raise ValueError("Must provide either points_timestamps or frame_timestamp")

    # For each camera, find the frame that is closest to the point's timestamp
    for camera in cameras:
        image_data, content_timestamp = camera.get_closest_content_at_timestamp(
            start_timestamp
        )

        intrinsics = camera.intrinsics
        camera_pose = camera.poses.interpolate([content_timestamp]).values[0]

        local_points = global_to_local(
            positions,
            camera_pose,
        )
        try:
            x, y, mask = project_distort(local_points, intrinsics)
        except Exception as e:
            print(f"Failed to project points for camera {camera.id}: {e}")
            continue

        if not hasattr(image_data, 'shape'):
            raise ValueError("image_data must have a shape attribute")
        img_shape: Tuple[int, ...] = tuple(image_data.shape)  # Convert to tuple for safe indexing

        x_arr = np.asarray(x, dtype=np.float64)
        y_arr = np.asarray(y, dtype=np.float64)
        mask_arr = np.asarray(mask, dtype=bool)

        mask = np.logical_and(
            mask_arr,
            np.logical_and(
                np.logical_and(x_arr >= 0, x_arr < img_shape[1]),
                np.logical_and(y_arr >= 0, y_arr < img_shape[0]),
            ),
        )

        index = np.argwhere(mask).reshape(-1)
        
        x_masked = x_arr[mask]
        y_masked = y_arr[mask]

        coords = np.column_stack([x_masked, y_masked])
        pixels = coords.astype(np.int32)

        if not hasattr(colors, 'shape'):
            raise ValueError("colors must have a shape attribute")
        if not hasattr(pixels, 'shape'):
            raise ValueError("pixels must have a shape attribute")
            
        colors[index] = image_data[pixels[:, 1], pixels[:, 0], :]
    return colors
