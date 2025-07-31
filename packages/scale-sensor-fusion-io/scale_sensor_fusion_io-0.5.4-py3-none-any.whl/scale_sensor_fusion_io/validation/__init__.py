from scale_sensor_fusion_io.model_converters.sfs import from_scene_spec_sfs
from .error import *
from .parser import *
from .validate import *


def parse_and_validate_scene(raw_scene: dict) -> ParseResult[Scene]:
    """
    1. parse dict to BS5.Scene
    2. convert to sfio.models.Scene
    3. run validations
    """
    parse_result = parse_scene_as_sfs(raw_scene)

    if not parse_result.success:
        return parse_result

    sfs_scene = parse_result.data

    try:
        scene = from_scene_spec_sfs(sfs_scene)
    except Exception as e:
        return ParseError.from_msg(
            f"Error converting to sfio.models.Scene. Error: {e}",
        )

    validate_result = validate_scene(scene)

    if not validate_result:
        # if no validate error, return parse result
        return ParseSuccess(data=scene)

    return ParseError(
        details=validate_result.details,
    )
