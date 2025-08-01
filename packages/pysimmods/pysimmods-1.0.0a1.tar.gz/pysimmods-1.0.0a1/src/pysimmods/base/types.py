from enum import Enum

from typing_extensions import TypeAlias, Union


class QControl(Enum):
    PRIORITIZE_P = 0
    PRIORITIZE_Q = 1


ModelParams: TypeAlias = dict[
    str, Union[float, int, str, bool, list[float] | QControl, "ModelParams"]
]

ModelInitVals: TypeAlias = dict[
    str, Union[float, int, str, bool, list[float], "ModelInitVals"]
]
