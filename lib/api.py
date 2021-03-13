#!/usr/bin/env python
import os
from importlib import import_module
from typing import Generator

from flask import Flask, Response, redirect, jsonify, url_for

provider = Flask(__name__)

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('lib.camera_' + os.environ['CAMERA']).Camera
else:
    from lib.camera_base import Camera


def get_base_path() -> str:
    """

    Returns:
        str: The base url path used during routing, i.e. the location in the nginx server.

    """
    return '/camerapi/'


def get_stream_path() -> str:
    """

    Returns:
        str: The path to the actual camera stream.

    """
    return get_base_path() + 'stream/'


def video_feed_generator(camera) -> Generator[str, None, None]:
    """
    
    Returns:
        Generator[str, None, None]: JPG camera images encoded as bitstring.
    """
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@provider.route(get_stream_path())
def video_feed() -> Response:
    """

    Returns:
        Response: JPG camera images encoded as HTML response for streaming to the web.
    """
    return Response(video_feed_generator(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')


@provider.route('/')
def root() -> Response:
    """

    Returns:
        Response: Endpoint for the landing page.
    """
    return redirect(get_stream_path())


@provider.route(get_base_path())
def index() -> Response:
    """

    Returns:
        Response: Endpoint for the video stream.
    """
    return redirect(get_stream_path())


@provider.route(get_base_path() + 'start_recording')
def start_recording() -> Response:
    """

    Starts the recording of the camera to disk on the server.

    Returns:
        Response: Endpoint for the video stream.
    """
    print("Start recording not implemented")
    return redirect(get_stream_path())


@provider.route(get_base_path() + 'stop_recording')
def stop_recording() -> Response:
    """

    Stops the recording of the camera to disk on the server.

    Returns:
        Response: Endpoint for the video stream.
    """
    print("Stop recording not implemented")
    return redirect(get_stream_path())


@provider.route(get_base_path() + 'start_streaming')
def start_streaming() -> Response:
    """

    Enables streaming of the live camera image to the web.

    Returns:
        Response: Endpoint for the video stream.
    """
    print("Start streaming not implemented")
    return redirect(get_stream_path())


@provider.route(get_base_path() + 'stop_streaming')
def stop_streaming() -> Response:
    """

    Disables streaming of the live camera image to the web.

    Returns:
        Response: Endpoint for the video stream.
    """
    print("Stop streaming not implemented")
    return redirect(get_stream_path())
