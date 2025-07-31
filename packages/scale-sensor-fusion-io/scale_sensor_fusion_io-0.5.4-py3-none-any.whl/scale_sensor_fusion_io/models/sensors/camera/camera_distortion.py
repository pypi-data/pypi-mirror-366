from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Mapping,
    Protocol,
    Type,
    Union,
)

from typing_extensions import TypeAlias


class DistortionModel(str, Enum):
    FISHEYE = "fisheye"
    MOD_KANNALA = "mod_kannala"
    CYLINDRICAL = "cylindrical"
    OMNIDIRECTIONAL = "omnidirectional"
    BROWN_CONRADY = "brown_conrady"
    EQUIRECTANGULAR = "equirectangular"
    MOD_EQUI_FISH = "mod_equi_fish"
    FISHEYE_RAD_TAN_THIN_PRISM = "fisheye_rad_tan_prism"
    FISHEYE_RADIAL_CUSTOM = "fisheye_radial_custom"
    FTHETA = "ftheta"


@dataclass
class DistortionParamsBase:
    model: DistortionModel


@dataclass
class BrownConradyParams(DistortionParamsBase):
    model: Literal[DistortionModel.BROWN_CONRADY] = DistortionModel.BROWN_CONRADY
    k1: float = 0
    k2: float = 0
    p1: float = 0
    p2: float = 0
    k3: float = 0
    k4: float = 0
    k5: float = 0
    k6: float = 0
    lx: float = 0
    ly: float = 0


@dataclass
class FisheyeParams(DistortionParamsBase):
    model: Literal[DistortionModel.FISHEYE] = DistortionModel.FISHEYE
    k1: float = 0
    k2: float = 0
    k3: float = 0
    k4: float = 0


@dataclass
class AppleFisheyeParams(DistortionParamsBase):
    model: Literal[DistortionModel.MOD_EQUI_FISH] = DistortionModel.MOD_EQUI_FISH
    k1: float = 0
    k2: float = 0
    k3: float = 0
    k4: float = 0


@dataclass
class AppleKannalaParams(DistortionParamsBase):
    model: Literal[DistortionModel.MOD_KANNALA] = DistortionModel.MOD_KANNALA
    k1: float = 0
    k2: float = 0
    k3: float = 0
    k4: float = 0


@dataclass
class CylindricalParams(DistortionParamsBase):
    model: Literal[DistortionModel.CYLINDRICAL] = DistortionModel.CYLINDRICAL

@dataclass
class EquirectangularParams(DistortionParamsBase):
    model: Literal[DistortionModel.EQUIRECTANGULAR] = DistortionModel.EQUIRECTANGULAR


@dataclass
class OmnidirectionalParams(DistortionParamsBase):
    model: Literal[DistortionModel.OMNIDIRECTIONAL] = DistortionModel.OMNIDIRECTIONAL
    k1: float = 0
    k2: float = 0
    k3: float = 0
    k4: float = 0
    p1: float = 0
    p2: float = 0
    xi: float = 0
    lx: float = 0
    ly: float = 0


@dataclass
class FisheyeRadTanThinPrismParams(DistortionParamsBase):
    model: Literal[
        DistortionModel.FISHEYE_RAD_TAN_THIN_PRISM
    ] = DistortionModel.FISHEYE_RAD_TAN_THIN_PRISM
    k1: float = 0
    k2: float = 0
    k3: float = 0
    k4: float = 0
    k5: float = 0
    k6: float = 0
    p1: float = 0
    p2: float = 0
    s1: float = 0
    s2: float = 0
    s3: float = 0
    s4: float = 0


@dataclass
class FisheyeRadialCustom(DistortionParamsBase):
    model: Literal[
        DistortionModel.FISHEYE_RADIAL_CUSTOM
    ] = DistortionModel.FISHEYE_RADIAL_CUSTOM
    k1: float = 0
    k2: float = 0
    k3: float = 0
    k4: float = 0
    k5: float = 0
    k6: float = 0
    p1: float = 0
    p2: float = 0
    dcx: float = 0
    dcy: float = 0


@dataclass
class FthetaParams(DistortionParamsBase):
    model: Literal[DistortionModel.FTHETA] = DistortionModel.FTHETA
    k1: float = 0
    k2: float = 0
    k3: float = 0
    k4: float = 0
    k5: float = 0


DistortionParams: TypeAlias = Union[
    BrownConradyParams,
    FisheyeParams,
    AppleFisheyeParams,
    AppleKannalaParams,
    CylindricalParams,
    EquirectangularParams,
    OmnidirectionalParams,
    FisheyeRadTanThinPrismParams,
    FisheyeRadialCustom,
    FthetaParams,
]

DISTORTION_PARAMETERS = {
    params
    for dist_models in DistortionParams.__args__  # type: ignore
    for params in dist_models.__dataclass_fields__.keys()
}


class DataClassProtocol(Protocol):
    __dataclass_fields__: ClassVar[dict]


def get_params_from_model(model: DistortionModel) -> Type[DistortionParams]:
    """
    Returns the dataclass for the given distortion model
    """
    supported_models: List[Type[DistortionParams]] = [
        BrownConradyParams,
        FisheyeParams,
        AppleFisheyeParams,
        AppleKannalaParams,
        CylindricalParams,
        EquirectangularParams,
        OmnidirectionalParams,
        FisheyeRadTanThinPrismParams,
        FisheyeRadialCustom,
        FthetaParams,
    ]

    return next(i for i in supported_models if i.model == model)


def extract_distortion_params(
    distortion: Union[DataClassProtocol, Mapping, dict]
) -> DistortionParams:
    """
    Generic helper to extract distortion params from untyped inputs.
    """
    distortion_fields: Dict[str, Any] = {}
    if isinstance(distortion, dict):
        distortion_fields = distortion
    elif isinstance(distortion, Mapping):
        distortion_fields = {k: v for k, v in distortion.items()}
    elif is_dataclass(distortion):
        distortion_fields = asdict(distortion)
    else:
        distortion_fields = distortion.__dict__

    model: DistortionModel = (
        distortion_fields.get("model")
        or distortion_fields.get("camera_model")
        or DistortionModel.BROWN_CONRADY
    )

    dataclass = get_params_from_model(model)
    # construct param dict for dataclass
    d = {}
    for key in dataclass.__dataclass_fields__:
        if (
            key in distortion_fields
            and key != "model"
            and distortion_fields[key] is not None
        ):
            d[key] = distortion_fields[key]
    return dataclass(**d)


# Define CameraDistortion dataclass
@dataclass
class CameraDistortion:
    """
    NOTE: model is here as helper attribute since it is already included in params
    """

    model: DistortionModel
    params: DistortionParams

    @staticmethod
    def from_values(model: str, values: List[float]) -> "CameraDistortion":
        """
        Creates a CameraDistortion IR from a model name and a list of values.

        NOTE: IMPORTANT: The values MUST be in the same order as the dataclass
        """
        # This will throw a ValueError if model is not a valid DistortionModel
        model_ = DistortionModel(model)
        ParamsClass = get_params_from_model(model_)

        # NOTE: This is a hack because neither of the following will work with
        # our current version of mypy
        #
        # 1. ParamsClass(model_, *values): Complains that model_ is not of type
        #    Literal[DistortionModel]
        # 2. params_dict = {...} (without the type hint): Complains that the
        #    Dict type is not compatible with the dataclass init. See:
        #    https://github.com/python/mypy/issues/5382
        # Therefore, we must type the dict as Dict[str, Any] to satisfy mypy
        params_dict: Dict = {
            k: v
            for k, v in zip(
                [k for k in ParamsClass.__dataclass_fields__.keys() if k != "model"],
                values,
            )
        }
        params = ParamsClass(**params_dict)
        return CameraDistortion(
            model=model_,
            params=params,
        )

    @staticmethod
    def from_dict(distortion_dict: Dict[str, Any]) -> "CameraDistortion":
        """
        Creates a CameraDistortion IR from a dict
        """
        model = DistortionModel(distortion_dict["model"])
        params = extract_distortion_params(distortion_dict)
        return CameraDistortion(
            model=model,
            params=params,
        )
