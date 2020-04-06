#!/usr/bin/env python

import inspect
import signal
import sys
import time
import socket

from sense_hat import SenseHat

from Camera import *
from RecordingsFolder import *
from WebStreaming import WebStreaming

sense = SenseHat()

recordingsFolder = RecordingsFolder()
camera = Camera(recordingsFolder.log_dir)
webstreaming = WebStreaming(camera)

camera_state_to_color_map: map = {
    CameraState.IDLE: (0, 0, 0),
    CameraState.STARTING_RECORD: (25, 25, 25),
    CameraState.RECORDING: (0, 25, 0),
    CameraState.STOPPING_RECORD: (25, 25, 0)
}


def signal_handler(sig, frame):
    """
    Signal handler for stop running

    :param sig:
    :param frame:
    """
    global camera
    recordingsFolder.write_to_log('Terminating', 'Ctrl+C pressed')
    camera.close_camera()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def function_name(stack_depth: int = 1) -> str:
    """
    Returns the function name.

    :param stack_depth:
    :return:
    """
    return str(inspect.stack()[stack_depth][3])


def on_error(err: Exception):
    """
    Called if an error occurs in any of the callbacks

    :param err:
    :return:
    """
    global camera

    recordingsFolder.write_to_log(function_name(2), err)
    camera.set_camera_state(CameraState.IDLE)


def display_camera_state(camera_state: CameraState):
    """
    Sets the sense hat matrix according to the recording state.
    """
    try:
        sense.clear(camera_state_to_color_map[camera_state])
        sense.low_light = True
    except Exception as err:
        recordingsFolder.write_to_log(function_name(), err)


def single_sensor_measurement(measurement_name: str, measurement_function):
    """
    Reads a measurement from the sense hat and logs it.

    :param measurement_name: The name of the measurement
    :param measurement_function: The measurement function
    """
    try:
        value = measurement_function()
        recordingsFolder.write_to_log(function_name(), measurement_name, value)
    except Exception as err:
        on_error(err)


def read_sensors(event):
    """
    Read the pressure, temperature and humidity from the sense hat and log.
    (Joystick key callback)

    :param event: the key input event
    """
    global camera
    if event.action != 'released':
        return

    sense.clear(0, 0, 255)
    single_sensor_measurement('Pressure', sense.get_pressure)
    single_sensor_measurement('Humidity', sense.get_humidity)
    single_sensor_measurement('Temperature (Humidity)', sense.get_temperature_from_humidity)
    single_sensor_measurement('Temperature (Pressure)', sense.get_temperature_from_pressure)
    display_camera_state(camera.camera_state)


def start_camera(event):
    """
    Method stub for camera starting later on
    (Joystick key callback)

    :param event: the key input event
    """
    global camera
    global webstreaming

    if event.action != 'released' or camera.camera_state is not CameraState.IDLE:
        return

    try:
        recordingsFolder.write_to_log(function_name(), 'Starting camera')
        display_camera_state(camera.set_camera_state(CameraState.STARTING_RECORD))
    except Exception as err:
        on_error(err)


def stop_camera(event):
    """
    Method stub for camera stopping later on
    (Joystick key callback)

    :param event: the key input event
    """
    global camera
    if event.action != 'released' or camera.camera_state is not CameraState.RECORDING:
        return

    try:
        recordingsFolder.write_to_log(function_name(), 'Stopping camera')
        display_camera_state(camera.set_camera_state(CameraState.STOPPING_RECORD))
    except Exception as err:
        on_error(err)


def toggle_streaming(event):
    """
    Toggles the web stream.
    """
    global webstreaming
    if event.action != 'released':
        return

    webstreaming.toggle_streaming()


def show_ip(event):
    """
    Displays the own ip for easy connect.
    """
    global webstreaming
    if event.action != 'released':
        return

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        output_string = str(ip) + ':' + str(webstreaming.address[1])
        recordingsFolder.write_to_log('Show IP', 'ip', output_string)
        sense.show_message(output_string)
    except Exception as err:
        recordingsFolder.write_to_log('Show IP', 'failed', err)
        sense.clear(255, 0, 0)


sense.show_message('Starting Nightsight', scroll_speed=0.05)
sense.clear()

# Register joystick callbacks
sense.stick.direction_left = start_camera
sense.stick.direction_right = stop_camera
sense.stick.direction_up = read_sensors
sense.stick.direction_down = show_ip
sense.stick.direction_middle = toggle_streaming  # Press the enter key


while True:
    try:
        camera.run()
    except Exception as err:
        recordingsFolder.write_to_log('Run', err)
    display_camera_state(camera.camera_state)
    time.sleep(1)
