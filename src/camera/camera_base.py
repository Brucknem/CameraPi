import abc
import logging
from threading import Thread
from time import sleep

from src.camera.camera_state import CameraState
from src.utils.observable import Observable
from src.utils.recordings_folder import RecordingsFolder
from src.utils.utils import is_raspbian, read_file_relative_to, \
    get_default_recordings_path

camera_state_to_allowed_state_map: map = {
    CameraState.OFF: (CameraState.IDLE,),
    CameraState.IDLE: (CameraState.RECORDING, CameraState.OFF),
    CameraState.RECORDING: (CameraState.RECORDING,
                            CameraState.STOPPING_RECORD),
    CameraState.STOPPING_RECORD: (CameraState.IDLE,)
}


def get_camera(chunk_length=300,
               recordings_path: str = get_default_recordings_path()):
    """
    Factory method for the camera interface
    """
    if is_raspbian():
        from src.camera.camera_pi import Camera
    else:
        from src.camera.camera_mock import Camera
    return Camera(chunk_length, recordings_path)


class CameraBase(Observable, metaclass=abc.ABCMeta):
    """
    Wrapper for the picamera.
    Never call directly. Call CameraBase.get_camera() to keep singleton.
    """

    def __init__(self, chunk_length: int = 5 * 60,
                 recordings_path: str = get_default_recordings_path()):
        """
        Constructor.
        """
        super().__init__()
        self.camera_state = CameraState.OFF

        self.chunk_length = chunk_length
        self.record_thread: Thread = None

        self.recordings_folder: RecordingsFolder = None
        self.set_recordings_folder(recordings_path)

        self.default_image = read_file_relative_to(
            "default_image.jpeg",
            __file__)
        self.streaming_thread = None
        self.is_streaming = False
        self.is_output_allowed = True

    def set_recordings_folder(self, recordings_path):
        """ Setter: recordings_folder """
        self.recordings_folder = RecordingsFolder(recordings_path)

    def __enter__(self):
        """
        Called via with
        """
        self.start_camera()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when with ended
        """
        self.stop_camera()

    def set_camera_state(self, new_mode: CameraState):
        """
        Setter for camera mode.
        """
        logging.debug(str(new_mode))
        self.camera_state = new_mode
        self.notify(state=self.camera_state)

    def start_camera(self):
        """
        Starts the camera.
        """
        logging.info('Start camera.')
        self.set_camera_state(CameraState.IDLE)

    def stop_camera(self):
        """
        Closes the camera.
        """
        logging.info('Stop camera.')
        self.set_camera_state(CameraState.OFF)

    def start_recording(self):
        """
        Start the recording.
        """
        logging.info('Start recording')
        if not self.camera_state == CameraState.IDLE:
            return

        if self.is_real_camera():
            if not self.can_write_recordings():
                self.set_recordings_folder(get_default_recordings_path())
            self.recordings_folder.create_new_recording()

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
        self.set_camera_state(CameraState.IDLE)
        self.record_thread = None
        return True

    def start_streaming(self, output):
        """
        Starts a stream to an output stream object.
        """
        logging.info('Start streaming')
        self.stop_streaming()
        self.streaming_thread = Thread(target=self._streaming_thread,
                                       args=(output,))
        self.streaming_thread.daemon = True
        self.streaming_thread.start()

    def _streaming_thread(self, output):
        """
        The default streaming thread.
        """
        self.is_streaming = True
        while self.is_streaming:
            if self.is_output_allowed:
                self.streaming_allowed(output)
            else:
                self.streaming_not_allowed(output)
        sleep(0.1)

    def streaming_allowed(self, output):
        """
        Writes to the buffer if the streaming is allowed
        """
        output.write(self.default_image)

    def streaming_not_allowed(self, output):
        """
        Writes to the buffer if the streaming is allowed
        """
        output.write(self.default_image)

    def stop_streaming(self):
        """
        Stops the streaming.
        """
        if self.streaming_thread:
            self.is_streaming = False
            self.streaming_thread.join()

    def is_real_camera(self):
        """
        Returns weather there is a real camera or a mock
        """
        return False

    def is_recording(self):
        """
        Is recording
        """
        return self.camera_state == CameraState.RECORDING

    def is_idle(self):
        """
        Is idle
        """
        return self.camera_state == CameraState.IDLE

    def can_write_recordings(self):
        """
        Checks if the recordings folder is writable
        """
        return self.recordings_folder.can_write_own_log_dir_path()
