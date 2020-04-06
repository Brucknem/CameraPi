import logging
import os
from enum import Enum
from pathlib import Path

from picamera import PiCamera

from Observable import Observable
from RecordingsFolder import RecordingsFolder
from Utils import *


class CameraState(Enum):
    """
    The camera state
    """
    IDLE = 1
    STARTING_RECORD = 2
    RECORDING = 3
    STOPPING_RECORD = 4
    CLOSED = 5


camera_state_to_allowed_state_map: map = {
    CameraState.IDLE: (CameraState.STARTING_RECORD,),
    CameraState.STARTING_RECORD: (CameraState.RECORDING,),
    CameraState.RECORDING: (CameraState.RECORDING, CameraState.STOPPING_RECORD),
    CameraState.STOPPING_RECORD: (CameraState.IDLE,)
}


class Camera(Observable):
    """
    Wrapper for the picamera.
    """

    def __init__(self, chunk_length: int = 5):
        """
        Constructor.
        """
        super().__init__()
        self.camera_state = CameraState.IDLE
        self.__camera = PiCamera()
        self.__camera.resolution = 1200, 900
        self.__camera.framerate = 30

        # self.__camera.vflip = True
        self.__base_recordings_folder = RecordingsFolder().log_dir
        self.__current_recordings_folder = RecordingsFolder().log_dir
        self.__chunk_lenght = chunk_length

        self.is_streaming = False

    def set_camera_state(self, new_mode: CameraState, force=False):
        """
        Setter for camera mode.
        """
        if not force and new_mode not in camera_state_to_allowed_state_map[self.camera_state]:
            return

        logging.info(str(new_mode))
        self.camera_state = new_mode
        self.notify(state=self.camera_state)

    def close_camera(self):
        """
        Closes the camera.
        """
        self.__camera.close()

    def start_recording(self):
        """
        Start the recording.
        """
        self.__current_recordings_folder = os.path.join(self.__base_recordings_folder, get_datetime_now_file_string())
        Path(self.__current_recordings_folder).mkdir(parents=True, exist_ok=True)

        self.__camera.start_preview()
        self.__camera.start_recording(self.get_chunk_path())
        self.set_camera_state(CameraState.RECORDING)

    def record(self):
        """
        Record functionality of the camera.
        """
        self.__camera.split_recording(self.get_chunk_path())
        self.__camera.wait_recording(self.__chunk_lenght)
        self.set_camera_state(CameraState.RECORDING)

    def stop_recording(self):
        """
        Stop the recording.
       """
        self.__camera.stop_recording()
        self.__camera.stop_preview()
        self.set_camera_state(CameraState.IDLE)

    def start_streaming(self, output):
        """
        Starts a stream to an output stream object.
        """
        if not self.is_streaming:
            self.__camera.start_recording(output, format='mjpeg', splitter_port=2)
            self.is_streaming = True
            return True
        return False

    def stop_streaming(self):
        """
        Stops the streaming.
        """
        if self.is_streaming:
            self.__camera.stop_recording(splitter_port=2)
            self.is_streaming = False

    def run(self):
        """
        The main run function for the camera.

        :return: the current camera state
        """

        try:
            if self.camera_state is CameraState.STARTING_RECORD:
                self.start_recording()
            elif self.camera_state is CameraState.RECORDING:
                self.record()
            elif self.camera_state is CameraState.STOPPING_RECORD:
                self.stop_recording()
        except Exception as err:
            logging.exception('Run: ' + str(err))
            self.set_camera_state(CameraState.IDLE, True)

    def get_chunk_path(self):
        """
        Returns the full path to the current chunk.
        :return:
        """
        return os.path.join(self.__current_recordings_folder, get_datetime_now_file_string() + '.h264')
