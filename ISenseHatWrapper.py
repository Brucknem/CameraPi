import logging
import socket

from ICamera import CameraState
from Observer import Observer

camera_state_to_color_map: map = {
    CameraState.IDLE: (0, 0, 0),
    CameraState.RECORDING: (0, 25, 0),
    CameraState.STOPPING_RECORD: (25, 25, 0)
}


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

        try:
            pixel_list = self.sense.get_pixels()
            self.sense.clear(0, 0, 255)

            pressure = self.sense.get_pressure
            humidity = self.sense.get_humidity
            temperature_humidity = self.sense.get_temperature_from_humidity
            temperature_pressure = self.sense.get_temperature_from_pressure

            values.update(single_sensor_measurement('Temperature (Pressure)',
                                                    temperature_pressure))
            values.update(single_sensor_measurement('Temperature (Humidity)',
                                                    temperature_humidity))
            values.update(single_sensor_measurement('Pressure', pressure))
            values.update(single_sensor_measurement('Humidity', humidity))
            self.sense.clear()
            self.sense.set_pixels(pixel_list)

        except Exception as err:
            logging.exception(err)

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

    def setup_callbacks(self, left=None, right=None, up=None, down=None, middle=None, message=None):
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
        except:
            pass
