import logging
import os
import time
from enum import Enum
from pathlib import Path
from threading import Thread

from picamera import PiCamera

from Observable import Observable
from RecordingsFolder import RecordingsFolder
from Utils import *


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
    CameraState.RECORDING: (CameraState.RECORDING, CameraState.STOPPING_RECORD),
    CameraState.STOPPING_RECORD: (CameraState.IDLE,)
}


class Camera(Observable):
    """
    Wrapper for the picamera.
    """

    def __init__(self, chunk_length: int = 5 * 60):
        """
        Constructor.
        """
        super().__init__()
        self.camera_state = CameraState.IDLE
        self.__camera = None

        self.__base_recordings_folder = RecordingsFolder().log_dir
        self.__current_recordings_folder = RecordingsFolder().log_dir
        self.__chunk_lenght = chunk_length

        self.output = None
        self.record_thread = None
        self.is_recording = False

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
        logging.info('Recovering camera')
        old_state = self.camera_state

        try:
            self.camera_state = CameraState.STOPPING_RECORD
            self.record_thread.join()
        except:
            logging.info('No thread found')

        self.camera_state = old_state

        try:
            self.__camera.close()
        except:
            logging.info('No camera found')

        self.__camera = PiCamera()
        self.__camera.resolution = 1200, 900
        self.__camera.framerate = 30

        if old_state is CameraState.RECORDING:
            self.start_recording()

        if self.output:
            self.start_streaming(self.output)

    def close_camera(self):
        """
        Closes the camera.
        """
        self.camera_state = CameraState.STOPPING_RECORD

        try:
            self.__camera.stop_recording()
            self.__camera.stop_preview()
        except:
            pass
        finally:
            self.__camera.close()

    def start_recording(self):
        """
        Start the recording.
        """
        if self.camera_state is not CameraState.IDLE:
            return
        logging.info('Start recording')
        self.set_camera_state(CameraState.RECORDING)

        self.__current_recordings_folder = os.path.join(self.__base_recordings_folder, get_datetime_now_file_string())
        Path(self.__current_recordings_folder).mkdir(parents=True, exist_ok=True)

        self.record_thread = Thread(target=self.record, args=())
        self.record_thread.daemon = True
        self.record_thread.start()

    def record(self):
        """
        Record functionality of the camera.
        """

        self.set_camera_state(CameraState.RECORDING)
        self.__camera.start_preview()
        self.__camera.start_recording(self.get_chunk_path())
        self.__camera.wait_recording(self.__chunk_lenght)

        try:
            while self.camera_state is CameraState.RECORDING:
                logging.info('Recording')
                self.__camera.split_recording(self.get_chunk_path())
                self.__camera.wait_recording(self.__chunk_lenght)
        except Exception as err:
            self.recover_camera()

    def stop_recording(self):
        """
        Stop the recording.
        """
        if self.camera_state is not CameraState.RECORDING:
            return
        logging.info('Stop recording')

        self.set_camera_state(CameraState.STOPPING_RECORD)
        self.__camera.stop_recording()
        self.__camera.stop_preview()
        self.set_camera_state(CameraState.IDLE)
        self.record_thread = None

    def start_streaming(self, output):
        """
        Starts a stream to an output stream object.
        """
        if not self.output:
            logging.info('Start streaming')
            self.output = output
            self.__camera.start_recording(self.output, format='mjpeg', splitter_port=2)
            return True
        return False

    def stop_streaming(self):
        """
        Stops the streaming.
        """
        if self.output:
            logging.info('Stop streaming')

            self.__camera.stop_recording(splitter_port=2)
            self.output = None

    def get_chunk_path(self):
        """
        Returns the full path to the current chunk.
        :return:
        """
        return os.path.join(self.__current_recordings_folder, get_datetime_now_file_string() + '.h264')
