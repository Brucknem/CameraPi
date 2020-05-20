import io
import json
import socketserver
import threading
from http import server
from threading import Condition

import jinja2

from src.camera.camera_base import CameraBase
from src.sense_hat_wrapper.sense_hat_wrapper_base import SenseHatWrapperBase
from src.utils.utils import read_cpu_temperature, read_ip

templateLoader = jinja2.PackageLoader("src.web", "templates")
templateEnv = jinja2.Environment(loader=templateLoader)

index_template = templateEnv.get_template('base.html')
settings_template = templateEnv.get_template('settings.html')

toggle_allow_streaming_url = '/96LTVesGktcbD7QfB8w74huCWdQQC' \
                             'eyHJhDAD9VHEhWnLuWDzc7aEQjeseuMe4pG'


class StreamingOutput(object):
    """
    The output for the camera web stream.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        """
        Write to the stream buffer.
        """
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


def on_start_stop_buttons(post_body):
    """
    Checks if there is a start or stop in the get values and
    calls the camera accordingly.
    """
    global web_streaming

    if 'start' in post_body:
        web_streaming.start_recording()
    elif 'stop' in post_body:
        web_streaming.stop_recording()


def read_measurements():
    """
    Reads the measurements.
    """
    global web_streaming
    if web_streaming.sense_hat:
        measurements = web_streaming.sense_hat.read_sensors()
    else:
        measurements = read_cpu_temperature()
    return measurements


class StreamingHandler(server.BaseHTTPRequestHandler):
    """
    Base Http request handler for the camera stream.
    """

    def finalize_response(self, html):
        """
        Finalizes the response and sets the necessary headers.
        """
        html_template_string = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(html_template_string)))
        self.end_headers()
        self.wfile.write(html_template_string)

    def process_request(self):
        """
        Processes a request.
        """
        global web_streaming

        measurements = read_measurements()

        values = {
            'is_recording': web_streaming.camera.is_recording(),
            'measurements': measurements,
            'can_write_recordings': web_streaming.camera.can_write_recordings(),
            'base_path': web_streaming.camera.recordings_folder.base_path,
            'ip': read_ip()
        }
        html = 'Error in path resolve.'
        if self.path == '/index.html':
            html = index_template.render(**values)
        elif self.path == '/settings.html':
            if not web_streaming.camera.is_output_allowed:
                self.redirect_to_index()
                return
            html = settings_template.render(**values)
        self.finalize_response(html)

    def do_GET(self):
        """
        REST Get handler.
        """
        if self.path == '/':
            self.redirect_to_index()
        if self.path == '/favicon.ico':
            self.finalize_response('')
        elif self.path == '/index.html' or self.path == '/settings.html':
            self.process_request()
        elif self.path == '/stream.mjpg':
            self.do_streaming()
        elif self.path == '/measurements_event_stream':
            self.do_measurement_update()
        elif self.path == '/buttons_event_stream':
            self.do_button_update()
        elif self.path == toggle_allow_streaming_url:
            web_streaming.camera.is_output_allowed = \
                not web_streaming.camera.is_output_allowed
            self.redirect_to_index()
        else:
            self.send_error(404)
            self.end_headers()

    def redirect_to_index(self):
        """
        Redirects to the index view
        """
        self.send_response(302)
        self.send_header('Location', '/index.html')
        self.end_headers()

    def do_POST(self):
        """
        REST Post handler
        """
        from urllib.parse import parse_qs

        length = int(self.headers.get('content-length'))
        field_data = self.rfile.read(length).decode('utf-8')
        post_body = parse_qs(field_data)

        if str.startswith(str(self.path), '/settings'):
            if web_streaming.camera.is_output_allowed:
                on_start_stop_buttons(post_body)
            self.send_response(302)
            self.send_header('Location', '/settings.html')
            self.end_headers()

    def do_streaming(self):
        """
        Writes the latest frame to the streaming output.
        """
        global web_streaming
        self.send_response(200)

        self.send_header('Age', str(0))
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type',
                         'multipart/x-mixed-replace; boundary=FRAME')
        self.end_headers()
        try:
            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', str(len(frame)))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')
        except Exception:
            pass

    def do_measurement_update(self):
        """
        Writes the latest measurements to the server sent event.
        """
        boundary = 'MEASUREMENTS'
        self.set_streaming_headers(boundary)
        self.send_streaming_content(boundary, read_measurements())

    def do_button_update(self):
        """
        Writes the latest button event to the server sent event.
        """
        global web_streaming
        boundary = 'BUTTONS'
        data = {
            'is_streaming_allowed': web_streaming.camera.is_output_allowed,
            'is_recording': web_streaming.camera.is_recording()
        }
        self.set_streaming_headers(boundary)
        self.send_streaming_content(boundary, data, 500)

    def send_streaming_content(self, boundary, payload, retry: int = 3000):
        """
        Sends the streaming content.
        """
        data = b'retry: ' + str(retry).encode() + b'\n'
        data += b'data: '
        data += json.dumps(payload).encode()
        data += b'\n\n'
        self.wfile.write(b'--' + boundary.encode() + b'\r\n')
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        self.wfile.write(b'\r\n')

    def set_streaming_headers(self, boundary):
        """
        Sends the streaming headers.
        """
        self.send_response(200)
        self.send_header('Age', str(0))
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type',
                         'text/event-stream; boundary=' + str(boundary))
        self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    """
    The streaming server for the camera web stream.
    """
    allow_reuse_address = True
    daemon_threads = True


class WebStreaming:
    """
    Wrapper for the camera web stream.
    Runs an asynchron thread for the web view.
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
        self.address = '', 8080
        self.camera: CameraBase = None
        self.server = StreamingServer(self.address, StreamingHandler)
        self.sense_hat: SenseHatWrapperBase = None
        self.thread = None

    def set_camera(self, camera):
        """
        Sets the camera object.
        """
        self.camera = camera
        self.start_streaming()

    def set_sense_hat(self, sense_hat: SenseHatWrapperBase):
        """
        Sets the camera object.
        """
        self.sense_hat = sense_hat

    def start_recording(self):
        """
        Starts the recording.
        :return:
        """
        if not self.camera:
            return

        self.camera.start_recording()

    def stop_recording(self):
        """
        Stops the recording.
        """
        if not self.camera:
            return

        self.camera.stop_recording()

    def start_streaming(self):
        """
        Starts the camera stream.
        """
        if not self.thread:
            self.thread = threading.Thread(target=self.stream, args=())
            self.thread.daemon = True
            self.thread.start()

        self.camera.start_streaming(output)

    def stream(self):
        """
        Starts the camera in streaming mode and
        starts the webserver to stream to.
        """
        try:
            self.server.serve_forever()
        finally:
            self.camera.stop_streaming()


def get_web_streaming(camera: CameraBase,
                      sense_hat: SenseHatWrapperBase = None):
    """
    Gets the package internal web streaming object.
    """
    global web_streaming
    web_streaming.set_camera(camera)
    web_streaming.sense_hat = sense_hat

    return web_streaming


output = StreamingOutput()
web_streaming = WebStreaming()
