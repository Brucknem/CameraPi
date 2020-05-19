import logging

from picamera import PiCamera

from src.camera.camera_base import CameraState, CameraBase
from src.utils.utils import get_default_recordings_path


class Camera(CameraBase):
    """
    Wrapper for the picamera.
    Never call directly. Call Camera.get_camera() to keep singleton.
    """

    def __init__(self, chunk_length: int = 5 * 60,
                 recordings_path: str = get_default_recordings_path()):
        """
        Constructor.
        """
        super().__init__(chunk_length, recordings_path)
        self.real_camera = None
        self.streaming_chunk_length = 2

    def start_camera(self):
        """ Overriding """
        self.real_camera = PiCamera()
        self.real_camera.resolution = 1200, 900
        self.real_camera.framerate = 30
        self.real_camera.start_preview()

        super().start_camera()

    def stop_camera(self):
        """
        Closes the camera.
        """
        logging.info('Stopping camera.')
        self.camera_state = CameraState.STOPPING_RECORD

        self.stop_streaming()
        self.stop_recording()

        try:
            self.real_camera.stop_preview()
        except Exception:
            logging.info('Camera not recording.')

        self.real_camera.close()
        self.real_camera = None
        super().stop_camera()

    def record(self):
        """
        Record functionality of the camera.
        """
        super().record()

        self.real_camera.start_recording(
            self.recordings_folder.get_next_chunk_path())
        self.real_camera.wait_recording(self.chunk_length)

        try:
            while self.camera_state is CameraState.RECORDING:
                logging.info('Recording')
                if not self.can_write_recordings():
                    self.set_recordings_folder(get_default_recordings_path())
                self.real_camera.split_recording(
                    self.recordings_folder.get_next_chunk_path())
                self.real_camera.wait_recording(self.chunk_length)
        except Exception as e:
            logging.error('Error in record thread', e=e)

    def stop_recording(self):
        """
        Stop the recording.
        """
        if not super().stop_recording():
            return
        self.real_camera.stop_recording()
        self.record_thread = None

    def streaming_allowed(self, output):
        """ Overriding """
        try:
            self.real_camera.start_recording(output,
                                             format='mjpeg',
                                             splitter_port=2)
            self.real_camera.wait_recording(self.streaming_chunk_length,
                                            splitter_port=2)
            self.real_camera.stop_recording(splitter_port=2)
        except Exception:
            logging.info('Non critical error while streaming')

    def is_real_camera(self):
        """ Overriding """
        return True
