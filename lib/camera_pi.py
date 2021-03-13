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

        if Camera.camera.closed:
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
        Camera.camera.start_recording('/home/pi/test_recordings/yeet.h264')
        for _ in Camera.camera.record_sequence(('/home/pi/test_recordings/yeet%d.h264' % i for i in range(1, 11)),
                                               splitter_port=2):
            Camera.camera.wait_recording(5)
