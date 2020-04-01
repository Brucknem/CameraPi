import inspect
import os
import shutil
import time
from datetime import datetime

from sense_hat import SenseHat

datetime_now = datetime.now()
sense = SenseHat()

file_date_format_string = '%Y_%m_%d_%H_%M_%S'
log_date_format_string = '%d-%m-%Y (%H:%M:%S)'

log_dir = '/mnt/harddrive/log/nightsight/'
log_file_name = datetime_now.strftime(file_date_format_string) + '.txt'
log_file = log_dir + log_file_name

is_camera_running: bool = False


def display_camera_running():
    """
    Sets the sense hat matrix according to the recording state.
    """
    global is_camera_running

    if is_camera_running:
        sense.clear(255, 255, 0)
        sense.low_light = True
    else:
        sense.clear()


def write_to_log(key: any, value: any = None, stack_depth: int = 1):
    """
    Write to log file.

    :param stack_depth:
    :param key: The key message that is written.
    :param value: An optional value
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


def single_sensor_measurement(measurement_name: str, measurement_function):
    """
    Reads a measurement from the sense hat and logs it.

    :param measurement_name: The name of the measurement
    :param measurement_function: The measurement function
    """
    try:
        value = measurement_function()
        write_to_log(measurement_name, value, 2)
    except Exception as err:
        write_to_log(err)


def read_sensors(event):
    """
    Read the pressure, temperature and humidity from the sense hat and log.
    (Joystick key callback)

    :param event: the key input event
    """

    if event.action == 'released':
        return

    sense.clear(0, 255, 0)
    single_sensor_measurement('Pressure', sense.get_pressure)
    single_sensor_measurement('Humidity', sense.get_humidity)
    single_sensor_measurement('Temperature (Humidity)', sense.get_temperature_from_humidity)
    single_sensor_measurement('Temperature (Pressure)', sense.get_temperature_from_pressure)
    display_camera_running()


def remove_all_logs(event):
    """
    Removes all log files.
    (Joystick key callback)

    :param event: the key input event
    """
    if event.action == 'released':
        return

    try:
        sense.clear(255, 0, 0)
        for filename in os.listdir(log_dir):
            if filename == log_file_name:
                continue
            file_path = os.path.join(log_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                write_to_log('Failed to delete %s: %s' % (file_path, e))
        display_camera_running()
    except Exception as err:
        write_to_log(err)


def start_camera(event):
    """
    Method stub for camera starting later on
    (Joystick key callback)

    :param event: the key input event
    """
    global is_camera_running
    if event.action == 'released' or is_camera_running:
        return

    try:
        write_to_log('Camera', 'started')

        is_camera_running = True
        display_camera_running()

    except Exception as err:
        write_to_log(err)


def stop_camera(event):
    """
    Method stub for camera stopping later on
    (Joystick key callback)

    :param event: the key input event
    """
    global is_camera_running
    if event.action == 'released' or not is_camera_running:
        return

    try:
        write_to_log('Camera', 'stopped')

        is_camera_running = False
        display_camera_running()

    except Exception as err:
        write_to_log(err)


# Register joystick callbacks
sense.stick.direction_left = read_sensors
sense.stick.direction_right = remove_all_logs
sense.stick.direction_up = start_camera
sense.stick.direction_down = stop_camera
sense.stick.direction_middle = sense.clear  # Press the enter key

write_to_log('Started monitoring')
sense.show_message('Started Nightsight', scroll_speed=0.05)
time.sleep(0.5)
sense.clear()

while True:
    pass  # This keeps the program running to receive joystick events
