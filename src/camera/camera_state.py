from enum import Enum


class CameraState(Enum):
    """
    The camera state
    """
    IDLE = 1
    RECORDING = 2
    STOPPING_RECORD = 3
