import logging

import numpy as np
from picamera import PiCamera

from src.camera.camera_base import CameraState, CameraBase
from src.utils.utils import get_default_recordings_path, \
    get_datetime_now_log_string


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

    def update_timestamp(self):
        """
        Updates the timestamp in the video recording.
        """
        self.real_camera.annotate_text = get_datetime_now_log_string()

    def wait_and_annotate_video_recording(self, chunk_length):
        """
        Waits and annotates the video recording with the current time stamp.
        """
        step = 0.2
        for _ in np.arange(0, chunk_length, step):
            if self.camera_state is not CameraState.RECORDING:
                return
            self.update_timestamp()
            self.real_camera.wait_recording(step)

    def record(self):
        """
        Record functionality of the camera.
        """
        super().record()
        if not self.can_write_recordings():
            logging.info('Fallback folder')
            self.set_recordings_folder(get_default_recordings_path())

        self.real_camera.start_recording(
            self.recordings_folder.get_next_chunk_path())
        self.wait_and_annotate_video_recording(self.chunk_length)

        try:
            while self.camera_state is CameraState.RECORDING:
                logging.info('Recording')
                if not self.can_write_recordings():
                    self.set_recordings_folder(get_default_recordings_path())
                self.real_camera.split_recording(
                    self.recordings_folder.get_next_chunk_path())
                self.wait_and_annotate_video_recording(self.chunk_length)
        except Exception as e:
            logging.error('Error in record thread')
            print(e)
            self.stop_recording()
            self.start_recording()
        self.real_camera.annotate_text = ''

    def stop_recording(self):
        """
        Stop the recording.
        """
        if not super().stop_recording():
            return
        try:
            self.real_camera.stop_recording()
        except Exception:
            pass

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
