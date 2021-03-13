import io
import time

import picamera

from lib.camera_base import Camera
import atexit


class Camera(Camera):
    """
    Raspberry Pi camera driver.
    """

    camera = None
    camera_opened = False

    @staticmethod
    def frames():
        """
        inherited
        """

        if not Camera.camera_opened:
            Camera.camera = picamera.PiCamera()
            Camera.camera_opened = True

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


def exit_handler():
    print("Closing Raspberry Pi camera.")
    Camera.camera.close()


atexit.register(exit_handler)
