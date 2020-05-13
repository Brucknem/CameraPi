import logging
import time

from src.camera.CameraBase import CameraState, CameraBase


class MockCamera(CameraBase):
    """
    Wrapper for the picamera.
    Never call directly. Call Camera.get_camera() to keep singleton.
    """

    def __init__(self, chunk_length: int = 5 * 60,
                 recordings_path: str = './recordings'):
        """
        Constructor.
        """
        super().__init__(chunk_length, recordings_path)

    def record(self):
        """ Overriding """
        super().record()

        while self.camera_state is CameraState.RECORDING:
            logging.info('Recording')
            time.sleep(1)
