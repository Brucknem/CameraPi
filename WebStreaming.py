import io
import logging
import socketserver
import threading
from http import server
from threading import Condition

PAGE = """\
<html>
<head>
<title>Nightsight Pi Streaming Demo</title>
</head>
<body>
<h1>Nightsight Pi Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
<hr>
<button>Start recording</button>
<button>Stop recording</button>
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

    def do_GET(self):
        """
        REST Get handler.
        """
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
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
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
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

    def __init__(self, camera):
        """
        Constructor.
        """
        self.address = ('', 8080)
        self.camera = camera
        self.server = StreamingServer(self.address, StreamingHandler)
        self.is_streaming = False
        self.start_streaming()

    def start_streaming(self):
        """
        Starts the webserver.
        :return:
        """
        if self.is_streaming:
            return

        thread = threading.Thread(target=self.stream, args=())
        thread.daemon = True
        thread.start()

    def stop_streaming(self):
        """
        Stops the webserver.
        """
        if not self.is_streaming:
            return

        self.server.shutdown()

    def toggle_streaming(self):
        """
        Toggles the webserver.
        """
        if self.is_streaming:
            self.stop_streaming()
        else:
            self.start_streaming()

    def stream(self):
        """
        Starts the camera in streaming mode and starts the webserver to stream to.
        """
        self.is_streaming = True
        self.camera.start_streaming(output)
        try:
            self.server.serve_forever()
        finally:
            self.camera.stop_streaming()
            self.is_streaming = False


output = StreamingOutput()
