import logging

from src.sense_hat.ISenseHatWrapper import ISenseHatWrapper, \
    single_sensor_measurement


class SenseHatWrapper(ISenseHatWrapper):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self):
        """
        Constructor.
        """
        from sense_hat import SenseHat
        super().__init__(SenseHat())

    def read_sensors(self):
        """ Overriding """
        values = super().read_sensors()

        try:
            pixel_list = self.physical_sense_hat.get_pixels()
            self.physical_sense_hat.clear(0, 0, 255)

            pressure = self.physical_sense_hat.get_pressure
            humidity = self.physical_sense_hat.get_humidity
            temperature_humidity = \
                self.physical_sense_hat.get_temperature_from_humidity
            temperature_pressure = \
                self.physical_sense_hat.get_temperature_from_pressure

            values.update(single_sensor_measurement('Temperature (Pressure)',
                                                    temperature_pressure))
            values.update(single_sensor_measurement('Temperature (Humidity)',
                                                    temperature_humidity))
            values.update(single_sensor_measurement('Pressure', pressure))
            values.update(single_sensor_measurement('Humidity', humidity))
            self.physical_sense_hat.clear()
            self.physical_sense_hat.set_pixels(pixel_list)

        except Exception as err:
            logging.exception(err)
        return values

    def is_real_sense_hat(self):
        """ Overriding """
        return True
