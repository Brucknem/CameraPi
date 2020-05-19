from enum import Enum


class CameraState(Enum):
    """
    The camera state
    """
    OFF = 0
    IDLE = 1
    RECORDING = 2
    STOPPING_RECORD = 3
