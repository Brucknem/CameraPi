import os
from enum import Enum
from pathlib import Path

from picamera import PiCamera

from Utils import *


class CameraState(Enum):
    """
    The camera state
    """
    IDLE = 1
    STARTING_RECORD = 2
    RECORDING = 3
    STOPPING_RECORD = 4


class Camera:
    """
    Wrapper for the picamera.
    """
    def __init__(self, recordings_folder: str, chunk_length: int = 60):
        """
        Constructor.
        """
        self.camera_state = CameraState.IDLE
        self.__camera = PiCamera()
        self.__camera.resolution = 1600, 1200
        # self.__camera.vflip = True
        self.__base_recordings_folder = recordings_folder
        self.__current_recordings_folder = recordings_folder
        self.__chunk_lenght = chunk_length

    def set_camera_state(self, new_mode: CameraState):
        """
        Setter for camera mode.

        :param new_mode:
        :return:
        """
        self.camera_state = new_mode
        return self.camera_state

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

        print('starting')

    def record(self):
        """
        Record functionality of the camera.
        """
        self.__camera.split_recording(self.get_chunk_path())
        self.__camera.wait_recording(self.__chunk_lenght)

    def stop_recording(self):
        """
        Stop the recording.
        """
        self.__camera.stop_recording()
        self.__camera.stop_preview()
        self.set_camera_state(CameraState.IDLE)

    def run(self):
        """
        The main run function for the camera.

        :return: the current camera state
        """
        if self.camera_state is CameraState.STARTING_RECORD:
            self.start_recording()
        elif self.camera_state is CameraState.RECORDING:
            self.record()
        elif self.camera_state is CameraState.STOPPING_RECORD:
            self.stop_recording()
        return self.camera_state

    def get_chunk_path(self):
        """
        Returns the full path to the current chunk.
        :return:
        """
        return os.path.join(self.__current_recordings_folder, get_datetime_now_file_string() + '.h264')
