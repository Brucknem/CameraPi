import logging
import os
import time
from enum import Enum
from pathlib import Path
from threading import Thread

from picamera import PiCamera

from ICamera import CameraState, ICamera
from Observable import Observable
from RecordingsFolder import RecordingsFolder
from Utils import *


class Camera(ICamera):
    """
    Wrapper for the picamera.
    """

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

    def record(self):
        """
        Record functionality of the camera.
        """
        super().set_camera_state()

        self.__camera.start_preview()
        self.__camera.start_recording(self.get_chunk_path())
        self.__camera.wait_recording(self.__chunk_length)

        try:
            while self.camera_state is CameraState.RECORDING:
                logging.info('Recording')
                self.__camera.split_recording(self.get_chunk_path())
                self.__camera.wait_recording(self.__chunk_length)
        except Exception as err:
            self.recover_camera()

    def stop_recording(self):
        """
        Stop the recording.
        """
        if not super().stop_recording():
            return
        self.__camera.stop_recording()
        self.__camera.stop_preview()
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

    def is_real_camera(self):
        """ Overriding """
        return True
