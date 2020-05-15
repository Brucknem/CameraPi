import logging

from picamera import PiCamera

from src.camera.CameraBase import CameraState, CameraBase


class PhysicalCamera(CameraBase):
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
        self.camera_state = CameraState.STOPPING_RECORD

        try:
            self.real_camera.stop_recording()
            self.real_camera.stop_preview()
        except Exception:
            pass
        finally:
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

    def start_streaming(self, output):
        """
        Starts a stream to an output stream object.
        """
        if not self.output:
            logging.info('Start streaming')
            self.output = output
            self.real_camera.start_recording(self.output,
                                             format='mjpeg',
                                             splitter_port=2)
            return True
        return False

    def stop_streaming(self):
        """
        Stops the streaming.
        """
        if self.output:
            logging.info('Stop streaming')

            self.real_camera.stop_recording(splitter_port=2)
            self.output = None

    def is_real_camera(self):
        """ Overriding """
        return True
