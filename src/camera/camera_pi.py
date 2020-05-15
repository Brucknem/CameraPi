import io
import logging

from src.camera.camera_base import CameraBase
from src.camera.camera_state import CameraState


class Camera(CameraBase):
    """
    Camera wrapper for the pi camera.

    Taken from:
    https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
    """

    def __init__(self, chunk_length: int = 5 * 60,
                 recordings_path: str = './recordings'):
        """
        Constructor.
        """
        from picamera import PiCamera

        super().__init__(chunk_length, recordings_path)
        self.pi_camera = PiCamera()
        self.pi_camera.resolution = 640, 480
        self.pi_camera.framerate = 30
        self.pi_camera.start_preview()
        self.stream = io.BytesIO()
        self.pi_camera.start_recording(self.stream, format='mjpeg',
                                       splitter_port=2)

    def __del__(self):
        """ Destructor """
        self.close_camera()

    def close_camera(self):
        self.stop_recording()
        try:
            self.pi_camera.stop_preview()
            self.pi_camera.stop_recording()
        except Exception:
            pass
        finally:
            self.pi_camera.close()

        self.pi_camera = None

    def frames(self):
        """ Overriding """
        # let camera warm up
        # return current frame

        while True:
            self.stream.seek(0)
            yield self.stream.read()

            # reset stream for next frame
            self.stream.seek(0)
            self.stream.truncate()

    def record(self):
        """
        Record functionality of the camera.
        """
        super().record()

        self.pi_camera.start_recording(
            self.recordings_folder.get_next_chunk_path())
        self.pi_camera.wait_recording(self.chunk_length)

        try:
            while self.camera_state is CameraState.RECORDING:
                logging.info('Recording')
                self.pi_camera.split_recording(
                    self.recordings_folder.get_next_chunk_path())
                self.pi_camera.wait_recording(self.chunk_length)
        except Exception as e:
            logging.error('Error in record thread', e=e)

    def stop_recording(self):
        """
        Stop the recording.
        """
        if not super().stop_recording():
            return
        self.pi_camera.stop_recording()
        self.record_thread = None

    def is_real_camera(self):
        """ Overriding """
        return True
