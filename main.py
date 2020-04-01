import inspect
from datetime import datetime

from sense_hat import SenseHat

file_date_format_string = '%Y_%m_%d_%H_%M_%S'
log_date_format_string = '%d-%m-%Y (%H:%M:%S)'
datetime_now = datetime.now()
sense = SenseHat()

log_file = '/home/pi/script_log_' + datetime_now.strftime(file_date_format_string) + '.txt'


def write_to_log(key: any, value: any = None, stack_depth: int = 1):
    """
    Write to log file.

    :param stack_depth:
    :param key: The key message that is written.
    :param value: An optional value
    :return:
    """
    try:
        with open(log_file, 'a+') as file:
            output_string: str = '[' + datetime.now().strftime(log_date_format_string) + ']\t'

            output_string += inspect.stack()[stack_depth][3] + ':\t'
            output_string += str(key)
            if value:
                output_string += ':\t' + str(value)

            output_string += '\n'
            print(output_string)
            file.write(output_string)
    except Exception as err:
        print(err)


write_to_log('Started monitoring')


def single_sensor_measurement(measurement_name: str, measurement_function):
    """
    Reads a measurement from the sense hat and logs it.

    :param measurement_name: The name of the measurement
    :param measurement_function: The measurement function
    :return:
    """
    try:
        value = measurement_function()
        write_to_log(measurement_name, value, 2)
    except Exception as err:
        write_to_log(err)


def pressure(event):
    """
    Read the pressure from the sense hat and log.
    (Joystick key callback)

    :param event: the key input event
    :return:
    """
    if event.action == 'released':
        return

    sense.clear(255, 0, 0)
    single_sensor_measurement('Pressure', sense.get_pressure)


def temperature(event):
    """
    Read the temperature from the sense hat and log.
    (Joystick key callback)

    :param event: the key input event
    :return:
    """
    if event.action == 'released':
        return

    sense.clear(0, 0, 255)
    single_sensor_measurement('Temperature (Humidity)', sense.get_temperature_from_humidity)
    single_sensor_measurement('Temperature (Pressure)', sense.get_temperature_from_pressure)


def humidity(event):
    """
    Read the humidity from the sense hat and log.
    (Joystick key callback)

    :param event: the key input event
    :return:
    """
    if event.action == 'released':
        return

    sense.clear(0, 255, 0)
    single_sensor_measurement('Humidity', sense.get_humidity)


def start_camera(event):
    """
    Method stub for camera starting later on
    (Joystick key callback)

    :param event: the key input event
    :return:
    """
    if event.action == 'released':
        return

    try:
        sense.clear(255, 255, 0)
        write_to_log('Camera', 'started')
    except Exception as err:
        write_to_log(err)


# Tell the program which function to associate with which direction
sense.stick.direction_up = humidity
sense.stick.direction_down = pressure
sense.stick.direction_left = temperature
sense.stick.direction_right = start_camera
sense.stick.direction_middle = sense.clear  # Press the enter key

while True:
    pass  # This keeps the program running to receive joystick events
