#!/usr/bin/env python
import logging
import signal
import sys
import time
import argparse

from Camera import *
from RecordingsFolder import *
from SenseHatWrapper import SenseHatWrapper
from SenseHatWrapperMock import SenseHatWrapperMock
from WebStreaming import get_webstreaming

out_path_default = './recordings'
parser = argparse.ArgumentParser(description='Camera Pi.')
parser.add_argument('--out',
                    nargs='?',
                    const=out_path_default,
                    type=str,
                    help='The output path for recordings and logs. Default: ' + out_path_default)
args = parser.parse_args()

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
logging.info('Started monitoring')

recordingsFolder = RecordingsFolder(args.out if args.out else out_path_default)

camera = Camera()
try:
    sense_hat_wrapper = SenseHatWrapper(camera)
except:
    sense_hat_wrapper = SenseHatWrapperMock()

webstreaming = get_webstreaming()
webstreaming.set_camera(camera)
webstreaming.set_sense_hat(sense_hat_wrapper)

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
    sense_hat_wrapper.clear()
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


sense_hat_wrapper.setup_callbacks(left=start_camera,
                                  right=stop_camera,
                                  up=start_streaming,
                                  down=stop_streaming,
                                  middle=show_ip,
                                  message='Started CameraPi')

while True:
    pass
