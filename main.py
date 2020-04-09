#!/usr/bin/env python
import logging
import signal
import sys
import time

from Camera import *
from RecordingsFolder import *
from SenseHatWrapper import SenseHatWrapper
from SenseHatWrapperMock import SenseHatWrapperMock
from WebStreaming import webstreaming

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
logging.info('Started monitoring')

recordingsFolder = RecordingsFolder()

camera = Camera()
webstreaming.set_camera(camera)
try:
    sense_hat_wrapper = SenseHatWrapper(camera)
except:
    sense_hat_wrapper = SenseHatWrapperMock()

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
    sense_hat_wrapper.sense.clear()
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

    if event.action != 'released':
        return

    try:
        camera.start_recording()
    except Exception as err:
        logging.exception(err)


def stop_camera(event):
    """
    Method stub for camera stopping later on
    (Joystick key callback)

    :param event: the key input event
    """
    global camera
    if event.action != 'released':
        return

    try:
        camera.stop_recording()
    except Exception as err:
        logging.exception(err)


def start_streaming(event):
    """
    Starts the web stream.
    """
    global webstreaming
    if event.action != 'released':
        return

    webstreaming.start_streaming()


def stop_streaming(event):
    """
    Stops the web stream.
    """
    global webstreaming
    if event.action != 'released':
        return

    webstreaming.stop_streaming()


def show_ip(event):
    """
    Displays the own ip for easy connect.
    """
    if event.action != 'released':
        return

    sense_hat_wrapper.show_ip()


# Register joystick callbacks
try:
    sense_hat_wrapper.sense.stick.direction_left = start_camera
    sense_hat_wrapper.sense.stick.direction_right = stop_camera
    sense_hat_wrapper.sense.stick.direction_up = start_streaming
    sense_hat_wrapper.sense.stick.direction_down = stop_streaming
    sense_hat_wrapper.sense.stick.direction_middle = show_ip  # Press the enter key

    sense_hat_wrapper.sense.show_message('Started Nightsight', scroll_speed=0.05)
    sense_hat_wrapper.sense.clear()
except:
    pass

while True:
    pass
