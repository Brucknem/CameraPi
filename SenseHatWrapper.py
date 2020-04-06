import logging
import socket

from sense_hat import SenseHat

from Camera import CameraState
from Observer import Observer
from RecordingsFolder import RecordingsFolder
from Utils import function_name

camera_state_to_color_map: map = {
    CameraState.IDLE: (0, 0, 0),
    CameraState.STARTING_RECORD: (25, 25, 25),
    CameraState.RECORDING: (0, 25, 0),
    CameraState.STOPPING_RECORD: (25, 25, 0)
}


def single_sensor_measurement(measurement_name: str, measurement_function):
    """
    Reads a measurement from the sense hat and logs it.

    :param measurement_name: The name of the measurement
    :param measurement_function: The measurement function
    """
    try:
        value = measurement_function()
        logging.info(str(measurement_name) + ': ' + str(value))
    except Exception as err:
        logging.exception(err)


class SenseHatWrapper(Observer):
    def __init__(self, camera):
        super().__init__()
        self.sense = SenseHat()
        self.camera = camera

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
        self.display_camera_state(kwargs['state'])

    def read_sensors(self):
        """
        Read the pressure, temperature and humidity from the sense hat and log.
    
        :param event: the key input event
        """
        try:
            self.sense.clear(0, 0, 255)
            single_sensor_measurement('Pressure', self.sense.get_pressure)
            single_sensor_measurement('Humidity', self.sense.get_humidity)
            single_sensor_measurement('Temperature (Humidity)',
                                      self.sense.get_temperature_from_humidity)
            single_sensor_measurement('Temperature (Pressure)',
                                      self.sense.get_temperature_from_pressure)
            # self.update(state=self.camera.camera_state)
            self.sense.clear()
        except Exception as err:
            logging.exception(err)

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
            logging.exception('Show IP failed: ', err)
            self.sense.clear(255, 0, 0)
