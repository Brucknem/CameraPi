from enum import Enum

from picamera import PiCamera


class CameraState(Enum):
    """
    The camera state
    """
    IDLE = 1
    STARTING_RECORD = 2
    RECORDING = 3
    STOPPING_RECORD = 4


class Camera:
    def __init__(self, recordings_folder: str):
        self.camera_state = CameraState.IDLE
        self.__camera = PiCamera()
        self.__camera.resolution = (1600, 1200)
        self.__camera.vflip = True
        self.__recordings_folder = recordings_folder

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
        Closes the camera
        """
        self.__camera.close()

    def start_recording(self):
        """
        Start the recording
        """
        # self.__camera.start_recording('file_name.h264')
        self.set_camera_state(CameraState.RECORDING)
        print('starting')

    def record(self):
        """
        Record functionality of the camera
        """
        pass

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
            self.set_camera_state(CameraState.IDLE)
        return self.camera_state
