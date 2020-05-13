import logging
from enum import Enum
from threading import Thread

from src.RecordingsFolder import RecordingsFolder
from src.utils.Observable import Observable


class CameraState(Enum):
    """
    The camera state
    """
    IDLE = 1
    RECORDING = 2
    STOPPING_RECORD = 3
    CLOSED = 4


camera_state_to_allowed_state_map: map = {
    CameraState.IDLE: (CameraState.RECORDING,),
    CameraState.RECORDING: (CameraState.RECORDING,
                            CameraState.STOPPING_RECORD),
    CameraState.STOPPING_RECORD: (CameraState.IDLE,)
}


def create_camera():
    """
    Factory method for the camera interface
    """
    try:
        from src.camera.Camera import Camera

        return Camera()
    except Exception:
        from src.camera.CameraMock import CameraMock

        return CameraMock()


class CameraFactory:
    """
    Factory for the camera interface
    """


class ICamera(Observable):
    """
    Wrapper for the picamera.
    """

    def __init__(self, chunk_length: int = 5 * 60):
        """
        Constructor.
        """
        super().__init__()
        self.real_camera = None
        self.camera_state = CameraState.IDLE

        self.chunk_length = chunk_length

        self.output = None
        self.record_thread: Thread = None
        self.is_recording: bool = False

        self.recover_camera()

    def set_camera_state(self, new_mode: CameraState):
        """
        Setter for camera mode.
        """
        logging.debug(str(new_mode))
        self.camera_state = new_mode
        self.notify(state=self.camera_state)

    def recover_camera(self):
        """
        Recovers the camera state after a failure
        """
        pass

    def close_camera(self):
        """
        Closes the camera.
        """
        pass

    def start_recording(self):
        """
        Start the recording.
        """
        if not self.camera_state == CameraState.IDLE:
            return

        logging.info('Start recording')
        if self.is_real_camera():
            RecordingsFolder().create_new_recording()

        self.record_thread = Thread(target=self.record, args=())
        self.record_thread.daemon = True
        self.record_thread.start()

    def record(self):
        """
        Record functionality of the camera.
        """
        self.set_camera_state(CameraState.RECORDING)

    def stop_recording(self):
        """
        Stop the recording.
        """
        if self.camera_state is not CameraState.RECORDING:
            return False
        logging.info('Stop recording')
        self.set_camera_state(CameraState.STOPPING_RECORD)
        # self.record_thread.join()
        self.record_thread = None
        self.set_camera_state(CameraState.IDLE)
        return True

    def start_streaming(self, output):
        """
        Starts a stream to an output stream object.
        """
        return True

    def stop_streaming(self):
        """
        Stops the streaming.
        """
        pass

    def is_real_camera(self):
        """
        Returns weather there is a real camera or a mock
        """
        return False
