import os

from flask import Flask, render_template, Response, request

app = Flask(__name__)


class EndpointAction(object):

    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        return self.action()


class FlaskAppWrapper(object):
    def __init__(self, camera):
        template_dir = os.path.dirname(
            os.path.abspath(os.path.dirname(__file__)))
        template_dir = os.path.join(template_dir, 'templates')
        self.app = Flask('Camera Pi Server', template_folder=template_dir)
        self.camera = camera
        self.add_endpoint('/', 'index', self.index_handler)
        self.add_endpoint('/video_feed', 'video_feed', self.video_feed)

    def run(self):
        self.app.run(host='0.0.0.0', debug=False, use_reloader=False)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))

    def index_handler(self):
        if 'start' in request.args:
            self.camera.start_recording()
        elif 'stop' in request.args:
            self.camera.stop_recording()

        return render_template('index.html',
                               is_recording=self.camera.is_recording())

    def gen(self):
        """
        Video streaming generator function.
        """
        while True:
            frame = self.camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def video_feed(self):
        """
        Video streaming route. Put this in the src attribute of an img tag.
        """
        return Response(self.gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
