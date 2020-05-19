from src.camera.camera_base import CameraBase
from src.sense_hat_wrapper.sense_hat_wrapper_base import SenseHatWrapperBase


class SenseHatWrapperMock(SenseHatWrapperBase):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self, camera: CameraBase,
                 message='Started CameraPi'):
        """
        Constructor.
        """
        from sense_emu import SenseHat
        super().__init__(SenseHat(), camera, message)
