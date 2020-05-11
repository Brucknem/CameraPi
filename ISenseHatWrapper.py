from ICamera import CameraState
from abc import ABC, abstractmethod


class ISenseHatWrapper(ABC):
    """
    Interface for the wrappers for the Sense Hat functions.
    """

    def display_camera_state(self, camera_state: CameraState):
        """
        Sets the sense hat matrix according to the recording state.
        """
        pass

    def update(self, **kwargs):
        """ Overriding """
        pass

    def read_sensors(self):
        """
        Read the pressure, temperature and humidity from the sense hat and log.
        """
        return {}

    def show_ip(self):
        """
        Displays the own ip for easy connect.
        """
        pass

    def clear(self):
        """
        Clears the matrix.
        """
        pass

    def setup_callbacks(self, left=None, right=None, up=None, down=None, middle=None, message=None):
        """
        Clears the matrix.
        """
        pass
