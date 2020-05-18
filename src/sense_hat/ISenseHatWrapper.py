import logging
import socket

from src.camera.CameraState import CameraState
from src.utils.Observer import Observer
from src.utils.Utils import read_cpu_temperature

camera_state_to_color_map: map = {
    CameraState.OFF: (0, 0, 25),
    CameraState.IDLE: (0, 0, 0),
    CameraState.RECORDING: (0, 25, 0),
    CameraState.STOPPING_RECORD: (25, 25, 0)
}


def create_sense_hat():
    """
    Factory method for the sense hat interface
    """

    try:
        from src.sense_hat.SenseHatWrapper import SenseHatWrapper

        return SenseHatWrapper()
    except Exception:
        from src.sense_hat.SenseHatWrapperMock import SenseHatWrapperMock

        return SenseHatWrapperMock()


class ISenseHatWrapper(Observer):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self, actual_sense_hat):
        """
        Constructor.
        """
        super().__init__()
        self.actual_sense_hat = actual_sense_hat

    def __del__(self):
        """
        Destructor.
        """
        self.clear()

    def display_camera_state(self, camera_state: CameraState):
        """
        Sets the sense hat matrix according to the recording state.
        """
        try:
            self.actual_sense_hat.clear(
                camera_state_to_color_map[camera_state])
            self.actual_sense_hat.low_light = True
        except Exception as err:
            logging.exception(err)

    def update(self, **kwargs):
        """
        @inheritdoc
        """
        super().update(**kwargs)
        if 'state' in kwargs:
            self.display_camera_state(kwargs['state'])

    def show_ip(self):
        """
        Displays the own ip for easy connect.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            output_string = str(ip) + ':' + str(8080)
            logging.info('IP: ' + output_string)
            self.actual_sense_hat.show_message(output_string)
        except Exception as err:
            logging.exception('Show IP failed: ' + str(err))
            self.actual_sense_hat.clear(255, 0, 0)

    def clear(self):
        """
        Clears the sense hat matrix.
        """
        self.actual_sense_hat.clear()

    def read_sensors(self):
        """
        Read the pressure, temperature and humidity from the sense hat and log.
        """

        values = read_cpu_temperature()
        return values

    def setup_callbacks(self,
                        left=None,
                        right=None,
                        up=None,
                        down=None,
                        middle=None,
                        message=None):
        """ Overriding """

        try:
            self.actual_sense_hat.stick.direction_left = left
            self.actual_sense_hat.stick.direction_right = right
            self.actual_sense_hat.stick.direction_up = up
            self.actual_sense_hat.stick.direction_down = down
            self.actual_sense_hat.stick.direction_middle = middle

            if message:
                self.actual_sense_hat.show_message(message,
                                                   scroll_speed=0.05)
            self.clear()
        except Exception:
            pass

    def is_real_sense_hat(self):
        """
        Check if instance is physical device
        """
        return False
