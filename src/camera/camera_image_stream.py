import logging
import pathlib
import time
from os import listdir
from os.path import join, isfile

from src.camera.camera_base import CameraBase
from src.camera.camera_state import CameraState


class Camera(CameraBase):
    """
    An emulated camera implementation that streams a repeated sequence of
    files at a rate of one frame per second.

    Taken from:
    https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
    """

    @staticmethod
    def get_default_images():
        """
        Loads the default images for the camera stream from disk.
        """
        my_path = join(pathlib.Path(__file__).parent.absolute(), 'stream_mock')
        stream_mock_files = [join(my_path, f) for f in listdir(my_path) if
                             isfile(join(my_path, f))]
        file_contents = []
        for file in stream_mock_files:
            with open(file, 'rb') as f:
                file_contents.append(f.read())
        return file_contents

    def __init__(self, chunk_length: int = 5 * 60,
                 recordings_path: str = './recordings'):
        """
        Constructor
        """
        super().__init__(chunk_length, recordings_path)
        self.images = Camera.get_default_images()

    def frames(self):
        """ Overriding """
        while True:
            time.sleep(1)
            yield self.images[
                int(time.time()) % len(self.images)]

    def record(self):
        """ Overriding """
        super().record()

        while self.camera_state is CameraState.RECORDING:
            logging.info('Recording')
            time.sleep(1)
