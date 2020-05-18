import logging

from sense_hat import SenseHat

from src.camera.CameraBase import CameraBase
from src.sense_hat.ISenseHatWrapper import ISenseHatWrapper


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


class SenseHatWrapper(ISenseHatWrapper):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self, camera: CameraBase):
        """
        Constructor.
        """
        super().__init__(SenseHat(), camera)

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

            values.update(single_sensor_measurement('Temperature (Pressure)',
                                                    temperature_pressure))
            values.update(single_sensor_measurement('Temperature (Humidity)',
                                                    temperature_humidity))
            values.update(single_sensor_measurement('Pressure', pressure))
            values.update(single_sensor_measurement('Humidity', humidity))
            self.actual_sense_hat.clear()
            self.actual_sense_hat.set_pixels(pixel_list)

        except Exception as err:
            logging.exception(err)
        return values

    def is_real_sense_hat(self):
        """ Overriding """
        return True
