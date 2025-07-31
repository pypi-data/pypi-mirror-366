from typing import List, Protocol, Tuple, TypeVar, Union, cast
from typing_extensions import assert_never

import numpy as np
import numpy.typing as npt
from scipy.spatial.transform import Rotation
from scale_sensor_fusion_io.models.sensors.camera import (
    AppleFisheyeParams,
    AppleKannalaParams,
    BrownConradyParams,
    DistortionModel,
    FisheyeParams,
    OmnidirectionalParams,
)
from scale_sensor_fusion_io.models.common import Point3D, QuaternionData
from scale_sensor_fusion_io.models.sensors.camera.camera_intrinsics import (
    CameraIntrinsics,
)


def global_to_local(
    pts: npt.NDArray[np.float64],
    cam_pose: npt.NDArray[np.float64],  # [x,y,z,qx,qy,qz,qw]
) -> npt.NDArray[np.float64]:
    local_pts = pts - cam_pose[0:3]
    rotation_matrix: npt.NDArray[np.float64] = Rotation.from_quat(
        cam_pose[3:7]
    ).as_matrix()
    return cast(npt.NDArray[np.float64], local_pts @ rotation_matrix)


def _smallest_pos_root(coeffs: npt.ArrayLike) -> float:
    roots = np.roots(coeffs)
    pos_roots: List[float] = sorted(roots[roots > 0])
    return pos_roots[0] if pos_roots else float("inf")


def _find_rsq_thresh(params: Union[BrownConradyParams, OmnidirectionalParams]) -> float:
    return _smallest_pos_root([7 * params.k3, 5 * params.k2, 3 * params.k1, 1])


def _find_theta_thresh(params: AppleFisheyeParams) -> float:
    return _smallest_pos_root([5 * params.k4, 4 * params.k3, 3 * params.k2, 0, 1])


def _find_theta_thresh_kannala(params: AppleKannalaParams) -> float:
    return np.pi / 2


def _find_theta2_thresh(params: FisheyeParams) -> float:
    return _smallest_pos_root(
        [9 * params.k4, 7 * params.k3, 5 * params.k2, 3 * params.k1, 1]
    )


def project_distort(
    pts: npt.NDArray, intrinsics: CameraIntrinsics
) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray[np.bool_]]:
    """
    given points in 3d relative to the camera, and a set of camera params
    returns a 3-tuple of distorted image x-coords, y-coords,
    and mask of whether or not the point was likely valid
    (ie within region where distorted radius varies monotonically with undistorted radius, and the point was in front of the camera plane)
    """
    epsilon = 1e-5

    p = intrinsics
    d = intrinsics.distortion.params if intrinsics.distortion else None

    camera_in_front = pts[:, 2] > 0

    if d and d.model is DistortionModel.OMNIDIRECTIONAL and d.xi:
        pts = pts / np.linalg.norm(pts, axis=1, keepdims=True)
        pts[:, 2] += d.xi

    # get x, y in homogeneous coordinates
    x = pts[:, 0] / pts[:, 2]
    y = pts[:, 1] / pts[:, 2]

    if (
        p.skew
    ):  # apply skew now so that we don't have to deal with it during distortion calculation
        x += y * p.skew / p.fx

    if not d or d.model is DistortionModel.CYLINDRICAL:
        # no distortion
        u = p.cx + p.fx * x
        v = p.cy + p.fy * y
        return u, v, camera_in_front

    if d.model is DistortionModel.EQUIRECTANGULAR:
        # Convert to spherical coordinates
        r = np.hypot(x, y)
        theta = np.arctan2(y, x)  # azimuthal angle
        phi = np.arccos(1 / r)  # polar angle

        # Equirectangular projection
        u = theta * p.fx + p.cx
        v = phi * p.fy + p.cy

        return u, v, camera_in_front

    if d.model is DistortionModel.MOD_EQUI_FISH:
        rho = np.hypot(x, y)
        theta = np.arctan(rho)
        m = np.where(rho < epsilon, 1, theta / rho)
        rad_dist_fac = np.polyval([d.k4, d.k3, d.k2, 0, 1], theta)
        u_d = p.fx * m * x * rad_dist_fac + p.cx
        v_d = p.fy * m * y * rad_dist_fac + p.cy
        return u_d, v_d, (theta < _find_theta_thresh(d)) & camera_in_front

    if d.model is DistortionModel.MOD_KANNALA:
        rho = np.hypot(x, y)
        theta = np.arctan(rho)
        ftheta = np.arctan(theta)
        ftheta2 = ftheta * ftheta
        r = np.polyval([d.k4, d.k3, d.k2, d.k1, 1], ftheta2) * ftheta
        rad_dist_fac = np.where(r < epsilon, 1, np.tan(r) / rho)
        u_d = p.fx * x * rad_dist_fac + p.cx
        v_d = p.fy * y * rad_dist_fac + p.cy
        return u_d, v_d, (theta < _find_theta_thresh_kannala(d)) & camera_in_front

    if d.model is DistortionModel.FISHEYE:
        rho = np.hypot(x, y)
        theta = np.arctan(rho)
        m = np.where(rho < epsilon, 1, theta / rho)
        t2 = theta * theta
        rad_dist_fac = np.polyval([d.k4, d.k3, d.k2, d.k1, 1], t2)
        u_d = p.fx * x * rad_dist_fac + p.cx
        v_d = p.fy * y * rad_dist_fac + p.cy
        return u_d, v_d, (theta < np.sqrt(_find_theta2_thresh(d))) & camera_in_front

    if (
        d.model is DistortionModel.BROWN_CONRADY
        or d.model is DistortionModel.OMNIDIRECTIONAL
    ):
        rsq = x * x + y * y
        x += d.lx
        y += d.ly
        rad_dist_fac = np.polyval([d.k3, d.k2, d.k1, 1], rsq)
        u_d = p.cx + p.fx * (
            x * rad_dist_fac + d.p1 * (rsq + 2 * x * x) + 2 * d.p2 * x * y
        )
        v_d = p.cy + p.fy * (
            y * rad_dist_fac + d.p2 * (rsq + 2 * y * y) + 3 * d.p1 * x * y
        )
        return u_d, v_d, (rsq < _find_rsq_thresh(d)) & camera_in_front

    if (
        d.model is DistortionModel.FISHEYE_RAD_TAN_THIN_PRISM
        or d.model is DistortionModel.FTHETA
        or d.model is DistortionModel.FISHEYE_RADIAL_CUSTOM
    ):
        raise Exception(f"Distortion model {d.model} is not supported")

    assert_never(d)
