import io
import logging
import time

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
        self.pi_camera.resolution = 1200, 900
        self.pi_camera.framerate = 30
        self.pi_camera.start_preview()

    def __del__(self):
        """ Destructor """
        self.camera_state = CameraState.STOPPING_RECORD

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
        with self.pi_camera as camera:
            # let camera warm up
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

    def record(self):
        """
        Record functionality of the camera.
        """
        super().record()

        self.pi_camera.start_preview()
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
        self.pi_camera.stop_preview()
        self.record_thread = None

    def is_real_camera(self):
        """ Overriding """
        return True
