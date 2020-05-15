from flask import Flask, render_template, Response

from src.camera.camera_base import CameraBase

app = Flask(__name__)
camera: CameraBase = None


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen():
    """Video streaming generator function."""
    global camera
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def run(actual_camera: CameraBase):
    global camera
    camera = actual_camera
    app.run(host='0.0.0.0', threaded=True)
