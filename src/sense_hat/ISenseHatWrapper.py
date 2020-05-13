import logging
import socket

from src.camera.ICamera import CameraState
from src.utils import Observer

camera_state_to_color_map: map = {
    CameraState.IDLE: (0, 0, 0),
    CameraState.RECORDING: (0, 25, 0),
    CameraState.STOPPING_RECORD: (25, 25, 0)
}


def create_sense_hat():
    """
    Factory method for the sense hat interface
    """

    try:
        from src.sense_hat import SenseHatWrapper

        return SenseHatWrapper()
    except Exception:
        from src.sense_hat import SenseHatWrapperMock

        return SenseHatWrapperMock()


def single_sensor_measurement(measurement_name: str, measurement_function):
    """
    Reads a measurement from the sense hat and logs it.

    :param measurement_name: The name of the measurement
    :param measurement_function: The measurement function
    """
    output = {measurement_name: None}
    try:
        value = measurement_function()
        logging.info(str(measurement_name) + ': ' + str(value))
        output[measurement_name] = value
    except Exception as err:
        logging.exception(err)
    return output


class ISenseHatWrapper(Observer):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
        self.sense = None

    def display_camera_state(self, camera_state: CameraState):
        """
        Sets the sense hat matrix according to the recording state.
        """
        try:
            self.sense.clear(camera_state_to_color_map[camera_state])
            self.sense.low_light = True
        except Exception as err:
            logging.exception(err)

    def update(self, **kwargs):
        """
        @inheritdoc
        """
        if 'state' in kwargs:
            self.display_camera_state(kwargs['state'])

    def read_sensors(self):
        """
        Read the pressure, temperature and humidity from the sense hat and log.
        """

        f = open("/sys/class/thermal/thermal_zone0/temp", "r")
        cpu = f.readline()
        values = {'Temperature (Chip)': str(int(cpu) / 1000) + ' \'C'}

        return values

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
            self.sense.show_message(output_string)
        except Exception as err:
            logging.exception('Show IP failed: ' + str(err))
            self.sense.clear(255, 0, 0)

    def clear(self):
        """ Overriding """
        self.sense.clear()

    def setup_callbacks(self,
                        left=None,
                        right=None,
                        up=None,
                        down=None,
                        middle=None,
                        message=None):
        """ Overriding """

        try:
            self.sense.stick.direction_left = left
            self.sense.stick.direction_right = right
            self.sense.stick.direction_up = up
            self.sense.stick.direction_down = down
            self.sense.stick.direction_middle = middle  # Press the enter key

            if message:
                self.sense.show_message(message, scroll_speed=0.05)
            self.clear()
        except Exception:
            pass

    def is_real_sense_hat(self):
        """
        Check if instance is physical device
        """
        return False
