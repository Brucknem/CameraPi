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
        Camera.camera.start_recording('./test_recordings/yeet.h264')
        Camera.camera.start_recording('1.h264')
        Camera.camera.wait_recording(1)
        for i in range(2, 11):
            Camera.camera.split_recording('%d.h264' % i)
            Camera.camera.wait_recording(1)
        Camera.camera.stop_recording()
