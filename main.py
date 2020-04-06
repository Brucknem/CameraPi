#!/usr/bin/env python
import logging
import signal
import sys
import time

from Camera import *
from RecordingsFolder import *
from SenseHatWrapper import SenseHatWrapper
from WebStreaming import webstreaming

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
logging.info('Started monitoring')

recordingsFolder = RecordingsFolder()

camera = Camera()
webstreaming.set_camera(camera)
sense_hat_wrapper = SenseHatWrapper(camera)

camera.attach(webstreaming)
camera.attach(sense_hat_wrapper)


def signal_handler(sig, frame):
    """
    Signal handler for stop running

    :param sig:
    :param frame:
    """
    global camera
    logging.info('Terminating: Ctrl+C pressed')
    camera.close_camera()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def read_sensors(event):
    """
    Read the pressure, temperature and humidity from the sense hat and log.
    (Joystick key callback)

    :param event: the key input event
    """
    global camera
    if event.action != 'released':
        return

    sense_hat_wrapper.read_sensors()


def start_camera(event):
    """
    Method stub for camera starting later on
    (Joystick key callback)

    :param event: the key input event
    """
    global camera

    if event.action != 'released' or camera.camera_state is not CameraState.IDLE:
        return

    try:
        logging.info('Starting camera')
        camera.set_camera_state(CameraState.STARTING_RECORD)
    except Exception as err:
        logging.exception(err)


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
        logging.info('Stopping camera')
        camera.set_camera_state(CameraState.STOPPING_RECORD)
    except Exception as err:
        logging.exception(err)


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
    if event.action != 'released':
        return

    sense_hat_wrapper.show_ip()


# Register joystick callbacks
sense_hat_wrapper.sense.stick.direction_left = start_camera
sense_hat_wrapper.sense.stick.direction_right = stop_camera
sense_hat_wrapper.sense.stick.direction_up = read_sensors
sense_hat_wrapper.sense.stick.direction_down = show_ip
sense_hat_wrapper.sense.stick.direction_middle = toggle_streaming  # Press the enter key

sense_hat_wrapper.sense.show_message('Started Nightsight', scroll_speed=0.05)
sense_hat_wrapper.sense.clear()

while True:
    camera.run()
    time.sleep(1)
