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


class ISenseHatWrapper(Observer):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self, actual_sense_hat, camera: CameraBase):
        """
        Constructor.
        """
        super().__init__()
        self.actual_sense_hat = actual_sense_hat
        self.camera = camera
        self.setup_callbacks(left=start_camera,
                             right=stop_camera,
                             up=start_streaming,
                             down=stop_streaming,
                             middle=show_ip,
                             message='Started CameraPi')

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


sense_hat: ISenseHatWrapper = None


def get_sense_hat(camera: CameraBase = None):
    """
    Factory method for the sense hat interface
    """
    global sense_hat
    if not sense_hat:
        if not camera:
            raise ValueError(
                'A camera must be given when instantiating a sense hat.')
        try:
            from src.sense_hat.sense_hat_wrapper import SenseHatWrapper

            sense_hat = SenseHatWrapper(camera)
        except Exception:
            from src.sense_hat.sense_hat_wrapper_mock import \
                SenseHatWrapperMock

            sense_hat = SenseHatWrapperMock(camera)
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

    sense_hat.camera.is_streaming_allowed = True


def stop_streaming(event):
    """
    Stops the web stream.
    """
    global sense_hat
    if event.action != 'released':
        return

    sense_hat.camera.is_streaming_allowed = False


def show_ip(event):
    """
    Displays the own ip for easy connect.
    """
    global sense_hat
    if event.action != 'released':
        return

    sense_hat.show_ip()
