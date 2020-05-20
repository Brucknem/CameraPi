import logging
from time import sleep

from src.camera.camera_base import CameraBase
from src.camera.camera_state import CameraState
from src.sense_hat_wrapper.sense_hat_wrapper_base import SenseHatWrapperBase

HUMIDITY = 'Humidity'

PRESSURE = 'Pressure'

TEMPERATURE_HUMIDITY_KEY = 'Temperature (Humidity)'

TEMPERATURE_PRESSURE_KEY = 'Temperature (Pressure)'


def single_sensor_measurement(measurement_name: str, measurement_function):
    """
    Reads a measurement from the sense hat and logs it.

    :param measurement_name: The name of the measurement
    :param measurement_function: The measurement function
    """
    output = {measurement_name: None}
    try:
        value = round(float(measurement_function()), 3)
        logging.info(
            str(measurement_name) + ': ' + str(value))
        output[measurement_name] = value
    except Exception as err:
        logging.exception(err)
    return output


class SenseHatWrapper(SenseHatWrapperBase):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self, camera: CameraBase,
                 message='Started CameraPi'):
        """
        Constructor.
        """
        from sense_hat import SenseHat
        self.actual_sense_hat = SenseHat()
        super().__init__(camera, message)

    def __del__(self):
        """
        Destructor.
        """
        self.clear()

    def setup(self, message):
        """
        Show the message and make specific setup.
        """
        super().setup(message)
        try:
            self.actual_sense_hat.stick.direction_left = self.start_recording
            self.actual_sense_hat.stick.direction_right = self.stop_recording
            self.actual_sense_hat.stick.direction_up = self.start_streaming
            self.actual_sense_hat.stick.direction_down = self.stop_streaming
            self.actual_sense_hat.stick.direction_middle = self.show_ip

            if message:
                self.actual_sense_hat.show_message(message,
                                                   scroll_speed=0.05)
            self.clear()
        except Exception:
            pass

    def read_sensors(self):
        """ Overriding """

        values = super().read_sensors()

        try:
            pixel_list = self.actual_sense_hat.get_pixels()
            self.actual_sense_hat.clear(0, 0, 255)

            pressure = self.actual_sense_hat.get_pressure
            humidity = self.actual_sense_hat.get_humidity
            temperature_humidity = \
                self.actual_sense_hat.get_temperature_from_humidity
            temperature_pressure = \
                self.actual_sense_hat.get_temperature_from_pressure

            values.update(single_sensor_measurement(TEMPERATURE_PRESSURE_KEY,
                                                    temperature_pressure))
            values.update(single_sensor_measurement(TEMPERATURE_HUMIDITY_KEY,
                                                    temperature_humidity))
            values.update(single_sensor_measurement(PRESSURE, pressure))
            values.update(single_sensor_measurement(HUMIDITY, humidity))
 

        except Exception as err:
            logging.exception(err)
        return values

    def is_real_sense_hat(self):
        """ Overriding """
        return True

    def get_matrix(self):
        """
        Returns the sense hat matrix.
        """
        return self.actual_sense_hat.get_pixels()

    def display_camera_state(self, camera_state: CameraState):
        """
        Sets the sense hat matrix according to the recording state.
        """
        color = super().display_camera_state(camera_state)
        try:
            self.actual_sense_hat.clear(color)
            self.actual_sense_hat.low_light = True
        except Exception as err:
            logging.exception(err)
            sleep(1)
        return color

    def show_ip(self, event=None):
        """
        Displays the own ip for easy connect.
        """
        if event and event.action != 'released':
            return

        ip = super().show_ip()
        if ip:
            self.actual_sense_hat.show_message(ip)
        else:
            self.actual_sense_hat.clear(255, 0, 0)
        return ip

    def clear(self):
        """
        Clears the sense hat matrix.
        """
        try:
            self.actual_sense_hat.clear()
        except Exception:
            pass

    def start_recording(self, event):
        """
        Method stub for camera starting later on
        (Joystick key callback)

        :param event: the key input event
        """
        if event.action != 'released':
            return

        try:
            self.camera.start_recording()
        except Exception as err:
            logging.exception(err)

    def stop_recording(self, event):
        """
        Method stub for camera stopping later on
        (Joystick key callback)

        :param event: the key input event
        """
        if event.action != 'released':
            return

        try:
            self.camera.stop_recording()
        except Exception as err:
            logging.exception(err)

    def start_streaming(self, event):
        """
        Starts the web stream.
        """
        if event.action != 'released':
            return

        self.camera.is_output_allowed = True

    def stop_streaming(self, event):
        """
        Stops the web stream.
        """
        if event.action != 'released':
            return

        self.camera.is_output_allowed = False
