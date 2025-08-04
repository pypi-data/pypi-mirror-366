from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional, NamedTuple

class SizeValueMode(str, Enum):
    ABSOLUTE = 'absolute'
    PERCENT = 'percent'
    FIT_CONTENT = 'fit-content'
    FIT_BACKGROUND_IMAGE = 'fit-background-image'

class SizeValue(NamedTuple):
    mode: SizeValueMode
    value: float = 0

@dataclass
class Size:
    width: SizeValue
    height: SizeValue
