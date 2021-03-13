import io
import time

from lib.camera_base import Camera
import atexit
import picamera


class Camera(Camera):
    """
    Raspberry Pi camera driver.
    """

    camera = None

    @staticmethod
    def frames():
        """
        inherited
        """

        Camera.camera = picamera.PiCamera()

        Camera.camera.resolution = 1200, 900
        Camera.camera.framerate = 30

        # let camera warm up
        time.sleep(2)

        stream = io.BytesIO()
        for _ in Camera.camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            # return current frame
            stream.seek(0)
            yield stream.read()

            # reset stream for next frame
            stream.seek(0)
            stream.truncate()

    @staticmethod
    def record():
        step = 0.2
        for _ in range(10):
            Camera.camera.wait_recording(step)
