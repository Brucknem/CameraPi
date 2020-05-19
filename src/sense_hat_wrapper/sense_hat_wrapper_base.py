import logging
import socket

from src.camera.camera_base import CameraBase
from src.camera.camera_state import CameraState
from src.utils.observer import Observer
from src.utils.utils import read_cpu_temperature

camera_state_to_color_map: map = {
    CameraState.OFF: (0, 0, 0),
    CameraState.IDLE: (0, 0, 25),
    CameraState.RECORDING: (0, 25, 0),
    CameraState.STOPPING_RECORD: (25, 25, 0)
}


class SenseHatWrapperBase(Observer):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self, camera: CameraBase,
                 message='Started CameraPi'):
        """
        Constructor.
        """
        super().__init__()
        self.camera = camera
        self.camera.attach(self)
        self.setup(message)

    def setup(self, message):
        """
        Show the message and make specific setup.
        """
        logging.info(message)

    def get_matrix(self):
        """
        Returns the sense hat matrix.
        """
        return []

    def display_camera_state(self, camera_state: CameraState):
        """
        Sets the sense hat matrix according to the recording state.
        """
        color = camera_state_to_color_map[camera_state]
        logging.info(
            'Displaying camera state: ' + str(camera_state) + "(" + str(
                color) + ')')
        return color

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
            return output_string
        except Exception as err:
            logging.exception('Show IP failed: ' + str(err))
            return None

    def read_sensors(self):
        """
        Read the pressure, temperature and humidity from the sense hat and log.
        """

        values = read_cpu_temperature()
        return values

    def is_real_sense_hat(self):
        """
        Check if instance is physical device
        """
        return False


sense_hat: SenseHatWrapperBase = None


def get_sense_hat(camera: CameraBase = None,
                  message='Started CameraPi'):
    """
    Factory method for the sense hat interface
    """
    global sense_hat
    if not sense_hat:
        if not camera:
            raise ValueError(
                'A camera must be given when instantiating a sense hat.')
        try:
            from src.sense_hat_wrapper.sense_hat_wrapper import SenseHatWrapper

            sense_hat = SenseHatWrapper(camera, message)
        except Exception:
            from src.sense_hat_wrapper.sense_hat_wrapper_mock import \
                SenseHatWrapperMock

            sense_hat = SenseHatWrapperMock(camera, message)
    return sense_hat


def read_sensors(event):
    """
    Read the pressure, temperature and humidity from the sense hat and log.
    (Joystick key callback)

    :param event: the key input event
    """
    global sense_hat
    if event.action != 'released':
        return

    try:
        return sense_hat.read_sensors()
    except Exception:
        return read_cpu_temperature()


def start_camera(event):
    """
    Method stub for camera starting later on
    (Joystick key callback)

    :param event: the key input event
    """
    global sense_hat
    if event.action != 'released':
        return

    try:
        sense_hat.camera.start_recording()
    except Exception as err:
        logging.exception(err)


def stop_camera(event):
    """
    Method stub for camera stopping later on
    (Joystick key callback)

    :param event: the key input event
    """
    global sense_hat
    if event.action != 'released':
        return

    try:
        sense_hat.camera.stop_recording()
    except Exception as err:
        logging.exception(err)


def start_streaming(event):
    """
    Starts the web stream.
    """
    global sense_hat
    if event.action != 'released':
        return

    sense_hat.camera.is_output_allowed = True


def stop_streaming(event):
    """
    Stops the web stream.
    """
    global sense_hat
    if event.action != 'released':
        return

    sense_hat.camera.is_output_allowed = False


def show_ip(event):
    """
    Displays the own ip for easy connect.
    """
    global sense_hat
    if event.action != 'released':
        return

    sense_hat.show_ip()
