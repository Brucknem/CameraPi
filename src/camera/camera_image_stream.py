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

    def __init__(self, chunk_length: int = 5 * 60,
                 recordings_path: str = './recordings'):
        """
        Constructor
        """
        super().__init__(chunk_length, recordings_path)

        print(pathlib.Path(__file__))
        self.images = [open(join(
            pathlib.Path(__file__).parent.absolute(),
            'stream_mock',
            stream_mock_file
        ), 'rb').read() for stream_mock_file in [f for f in listdir(
            join(pathlib.Path(__file__).parent.absolute(), 'stream_mock')) if
                                                 isfile(join(join(pathlib.Path(
                                                     __file__).parent.absolute(),
                                                                  'stream_mock'),
                                                             f))]]

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
