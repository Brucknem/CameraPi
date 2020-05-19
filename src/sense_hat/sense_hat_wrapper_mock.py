from src.camera.camera_base import CameraBase
from src.sense_hat.sense_hat_wrapper_base import ISenseHatWrapper


class SenseHatWrapperMock(ISenseHatWrapper):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self, camera: CameraBase):
        """
        Constructor.
        """
        from sense_emu import SenseHat
        super().__init__(SenseHat(), camera)
