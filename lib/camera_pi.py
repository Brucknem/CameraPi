import io
import threading
import time

from lib.camera_base import Camera
import atexit
import picamera


class Camera(Camera):
    """
    Raspberry Pi camera driver.
    """

    camera = None
    is_recording = False
    record_splitter_port = 2

    @staticmethod
    def frames():
        """
        inherited
        """

        if not Camera.camera or Camera.camera.closed:
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
        record_thread = threading.Thread(target=Camera.record_thread)
        record_thread.daemon = True
        record_thread.start()

    @staticmethod
    def record_thread():
        try:
            chunk = 3
            step = 0.5

            print("Recording is on")
            for _ in Camera.camera.record_sequence(
                    ('/home/pi/test_recordings/yeet%d.h264' % i for i in range(10000000)),
                    splitter_port=Camera.record_splitter_port):
                Camera.is_recording = True
                for i in range(int(chunk / step)):
                    if not Camera.is_recording:
                        Camera.stop_recording()
                        return
                    Camera.camera.wait_recording(step, splitter_port=Camera.record_splitter_port)
            Camera.stop_recording()
        except picamera.PiCameraAlreadyRecording as e:
            print(e)
        except AttributeError as e:
            print(e)

    @staticmethod
    def stop_recording():
        try:
            Camera.camera.stop_recording(splitter_port=Camera.record_splitter_port)
        except picamera.PiCameraNotRecording as e:
            print(e)
        except AttributeError as e:
            print(e)
        Camera.is_recording = False
        print("Recording is off")
