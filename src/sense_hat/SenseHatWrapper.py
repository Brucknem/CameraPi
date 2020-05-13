import logging

from src.sense_hat import ISenseHatWrapper, \
    single_sensor_measurement


class SenseHatWrapper(ISenseHatWrapper):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
        from src.sense_hat import SenseHat
        self.sense = SenseHat()

    def read_sensors(self):
        """ Overriding """
        values = super().read_sensors()

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

    def is_real_sense_hat(self):
        """ Overriding """
        return True
