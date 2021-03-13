import pathlib
import time

from lib.camera_base import Camera
from lib.data_provider import get_data_path


class Camera(Camera):
    """
    A mock camera that replays images from disk, i.e. mocks the streaming functionality.

    Attributes:
        The mock image frames.
    """

    images = [open(pathlib.Path(get_data_path(), f + '.jpg'), 'rb').read() for f in ['1', '2', '3']]

    @staticmethod
    def frames() -> bytes:
        """

        Returns:
            str: The bytes representation of the mock images.

        """
        while True:
            time.sleep(1)
            yield Camera.images[int(time.time()) % 3]
