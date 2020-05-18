#!/usr/bin/env python
import argparse
import logging
import signal
import sys

from src.camera.CameraBase import get_camera
from src.sense_hat.ISenseHatWrapper import get_sense_hat
from src.web.WebStreaming import get_web_streaming


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
sense_hat = get_sense_hat(camera)
web_streaming = get_web_streaming(camera, sense_hat)

with camera:
    camera.attach(web_streaming)
    camera.attach(sense_hat)
    while True:
        pass
