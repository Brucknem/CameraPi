import pathlib
import time
from os import listdir
from os.path import join, isfile

from src.camera.base_camera import BaseCamera


class Camera(BaseCamera):
    """An emulated camera implementation that streams a repeated sequence of
    files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""
    """
    https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
    """

    def __init__(self):
        super().__init__()
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
        while True:
            time.sleep(1)
            yield self.images[
                int(time.time()) % len(self.images)]
