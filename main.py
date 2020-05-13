#!/usr/bin/env python
import argparse
import logging
import signal
import sys

from src.WebStreaming import get_web_streaming
from src.camera.CameraBase import get_camera
from src.sense_hat.ISenseHatWrapper import create_sense_hat


def signal_handler(sig, frame):
    """
    Signal handler for stop running

    :param sig:
    :param frame:
    """
    global camera
    logging.info('Terminating: Ctrl+C pressed')
    camera.close_camera()
    sense_hat.clear()
    sys.exit(0)


def read_sensors(event):
    """
    Read the pressure, temperature and humidity from the sense hat and log.
    (Joystick key callback)

    :param event: the key input event
    """
    global camera
    if event.action != 'released':
        return

    sense_hat.read_sensors()


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
    global web_streaming
    if event.action != 'released':
        return

    web_streaming.start_streaming()


def stop_streaming(event):
    """
    Stops the web stream.
    """
    global web_streaming
    if event.action != 'released':
        return

    web_streaming.stop_streaming()


def show_ip(event):
    """
    Displays the own ip for easy connect.
    """
    if event.action != 'released':
        return

    sense_hat.show_ip()


signal.signal(signal.SIGINT, signal_handler)

chunk_length = 5 * 60
parser = argparse.ArgumentParser(description='Camera Pi.')
parser.add_argument('-c',
                    '--chunk_length',
                    nargs='?',
                    type=int,
                    help='The length of the video chunks [s]. '
                         'Default: ' + str(chunk_length) + ' s')
recordings_path = './recordings'
parser.add_argument('-o',
                    '--out',
                    nargs='?',
                    type=str,
                    help='The output path for recordings and logs. '
                         'Default: ' + recordings_path)
args = parser.parse_args()
chunk_length = \
    args.chunk_length if args.chunk_length else chunk_length
recordings_path = \
    args.out if args.out else recordings_path

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    level=logging.INFO)
logging.info('Started monitoring')

camera = get_camera(chunk_length, recordings_path)
sense_hat = create_sense_hat()

web_streaming = get_web_streaming()
web_streaming.set_camera(camera)
web_streaming.set_sense_hat(sense_hat)

camera.attach(web_streaming)
camera.attach(sense_hat)

sense_hat.setup_callbacks(left=start_camera,
                          right=stop_camera,
                          up=start_streaming,
                          down=stop_streaming,
                          middle=show_ip,
                          message='Started CameraPi')
with camera:
    while True:
        pass
