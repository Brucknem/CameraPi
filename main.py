#!/usr/bin/env python
import argparse
import logging
import signal
import sys

from src.camera.camera_base import get_camera
from src.sense_hat_wrapper.sense_hat_wrapper_base import get_sense_hat
from src.utils.utils import get_default_recordings_path
from src.web.web_streaming import get_web_streaming


def signal_handler(sig, frame):
    """
    Signal handler for stop running

    :param sig:
    :param frame:
    """
    global camera
    logging.info('Terminating: Ctrl+C pressed')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

chunk_length = 5 * 60
parser = argparse.ArgumentParser(description='Camera Pi.')
parser.add_argument('-c',
                    '--chunk_length',
                    nargs='?',
                    type=int,
                    help='The length of the video chunks [s]. '
                         'Default: ' + str(chunk_length) + ' s')
recordings_path = get_default_recordings_path()
parser.add_argument('-o',
                    '--out',
                    nargs='?',
                    type=str,
                    help='A semi-colon separated list of absolute paths that '
                         'should be written to in order. '
                         'If none of the paths is writable the fallback path '
                         'is ' + get_default_recordings_path())
args = parser.parse_args()
chunk_length = \
    args.chunk_length if args.chunk_length else chunk_length
recordings_path = \
    args.out if args.out else recordings_path

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    level=logging.INFO)
logging.info('Started monitoring')

camera = get_camera(chunk_length, recordings_path)

with camera:
    sense_hat = get_sense_hat(camera)
    web_streaming = get_web_streaming(camera, sense_hat)
    while True:
        pass
