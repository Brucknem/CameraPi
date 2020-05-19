import io
import socketserver
import threading
from http import server
from threading import Condition

from jinja2 import Template

from src.camera.camera_base import CameraBase
from src.sense_hat.sense_hat_wrapper_base import ISenseHatWrapper
from src.utils.observer import Observer
from src.utils.utils import read_cpu_temperature, read_file_relative_to

index_template_string = read_file_relative_to("templates/index.html",
                                              __file__, decode=True)
template = Template(index_template_string)


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


class StreamingHandler(server.BaseHTTPRequestHandler):
    """
    Base Http request handler for the camera stream.
    """

    def set_response(self):
        """
        Sets the common response headers and content.
        :return:
        """
        global web_streaming

        if web_streaming.sense_hat:
            measurements = web_streaming.sense_hat.read_sensors()
        else:
            measurements = read_cpu_temperature()

        # Render HTML Template String
        html_template_string = template.render(
            is_recording=web_streaming.camera.is_recording(),
            measurements=measurements)
        html_template_string = html_template_string.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(html_template_string)))
        self.end_headers()
        self.wfile.write(html_template_string)

    def do_GET(self):
        """
        REST Get handler.
        """
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif str.startswith(str(self.path), '/index.html'):
            from urllib.parse import parse_qs
            try:
                get_data = parse_qs(str.split(self.path, '?')[1])
                if 'start' in get_data:
                    web_streaming.start_recording()
                if 'stop' in get_data:
                    web_streaming.stop_recording()

            except IndexError:
                pass
            self.set_response()
        elif self.path == '/stream.mjpg':
            self.do_streaming()

        else:
            self.send_error(404)
            self.end_headers()

    def do_streaming(self):
        """
        Writes the latest frame to the streaming output.
        """
        global web_streaming
        self.send_response(200)

        self.send_header('Age', 0)
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
                self.send_header('Content-Length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')
        except Exception:
            pass


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    """
    The streaming server for the camera web stream.
    """
    allow_reuse_address = True
    daemon_threads = True


class WebStreaming(Observer):
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
        self.sense_hat: ISenseHatWrapper = None
        self.thread = None

    def set_camera(self, camera):
        """
        Sets the camera object.
        """
        self.camera = camera
        self.start_streaming()

    def set_sense_hat(self, sense_hat: ISenseHatWrapper):
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

    def update(self, **kwargs):
        """
        @inheritdoc
        """
        super().update(**kwargs)
        if 'restart' in kwargs:
            pass


def get_web_streaming(camera: CameraBase, sense_hat: ISenseHatWrapper = None):
    """
    Gets the package internal web streaming object.
    """
    global web_streaming
    web_streaming.set_camera(camera)
    web_streaming.sense_hat = sense_hat

    return web_streaming


output = StreamingOutput()
web_streaming = WebStreaming()
