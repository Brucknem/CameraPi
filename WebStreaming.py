import io
import logging
import socketserver
import threading
from http import server
from threading import Condition

from Camera import CameraState
from Observer import Observer

PAGE_TOP = """\
<!doctype html>
<html lang="en">
  <head>
"""

PAGE_REFRESH = """\
<meta http-equiv="refresh" content="5" />
"""

PAGE_MIDDLE = """\
</head>
<body width="100%" style="text-align:center; content-align:center; font-size:xx-large">
<h1>Nightsight Pi Streaming</h1>
<img src="stream.mjpg" width="100%" />
<br><br>
<form action = "" method = "post">
"""

START_RECORDING = '<input style="font-size:xx-large" class="button" type="submit" value="Start recording" ' \
                  'name="start" onclick=""></input> '
STOP_RECORDING = '<input style="font-size:xx-large" class="button" type="submit" value="Stop recording" name="stop" ' \
                 'onclick=""></input> '

START_RECORDING_DISABLED = '<input style="font-size:xx-large" disabled class="button" type="submit" value="Start ' \
                           'recording" name="start" onclick=""></input> '
STOP_RECORDING_DISABLED = '<input style="font-size:xx-large" disabled class="button" type="submit" value="Stop ' \
                          'recording" name="stop" onclick=""></input> '

PAGE_BOTTOM = """\
<br><br>
<input style="font-size:xx-large" class="button" type="submit" value="Refresh page" name="refresh" onclick=""></input>
</form>
</body>
</html>
"""


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
        global webstreaming

        content = PAGE_TOP.encode('utf-8')

        if webstreaming.camera.camera_state is CameraState.STOPPING_RECORD:
            content += PAGE_REFRESH.encode('utf-8')

        content = PAGE_MIDDLE.encode('utf-8')

        if webstreaming.camera.camera_state is CameraState.RECORDING:
            content += START_RECORDING_DISABLED.encode('utf-8')
            content += STOP_RECORDING.encode('utf-8')
        elif webstreaming.camera.camera_state is CameraState.IDLE:
            content += START_RECORDING.encode('utf-8')
            content += STOP_RECORDING_DISABLED.encode('utf-8')
        else:
            content += START_RECORDING_DISABLED.encode('utf-8')
            content += STOP_RECORDING_DISABLED.encode('utf-8')

        content += PAGE_BOTTOM.encode('utf-8')

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        """
        REST Post handler.
        """
        global webstreaming

        if self.path == '/index.html':
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself

            post_data = post_data.decode('utf-8')
            if 'start' in post_data:
                webstreaming.start_recording()
            if 'stop' in post_data:
                webstreaming.stop_recording()
            self.set_response()

        else:
            self.send_error(404)
            self.end_headers()

    def do_GET(self):
        """
        REST Get handler.
        """
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            self.set_response()
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
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
            except Exception as e:
                pass
                # logging.warning(
                #     'Removed streaming client %s: %s',
                #     self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


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
        self.camera = None
        self.server = StreamingServer(self.address, StreamingHandler)

    def set_camera(self, camera):
        """
        Sets the camera object.
        """
        self.camera = camera
        self.start_streaming()

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
        Starts the webserver.
        :return:
        """
        if not self.camera:
            return

        thread = threading.Thread(target=self.stream, args=())
        thread.daemon = True
        thread.start()

    def stop_streaming(self):
        """
        Stops the webserver.
        """
        if not self.camera:
            return

        self.server.shutdown()

    def stream(self):
        """
        Starts the camera in streaming mode and starts the webserver to stream to.
        """
        if self.camera.start_streaming(output):
            try:
                self.server.serve_forever()
            finally:
                self.camera.stop_streaming()

    def update(self, **kwargs):
        """
        @inheritdoc
        """
        if 'restart' in kwargs:
            pass


def get_webstreaming():
    global webstreaming
    return webstreaming


output = StreamingOutput()
webstreaming = WebStreaming()
