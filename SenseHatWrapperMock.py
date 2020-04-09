from Camera import CameraState
from Observer import Observer


class SenseHatWrapperMock(Observer):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()

    def display_camera_state(self, camera_state: CameraState):
        """
        Sets the sense hat matrix according to the recording state.
        """
        pass

    def update(self, **kwargs):
        """
        @inheritdoc
        """
        pass

    def read_sensors(self):
        """
        Read the pressure, temperature and humidity from the sense hat and log.

        :param event: the key input event
        """
        pass

    def show_ip(self):
        """
        Displays the own ip for easy connect.
        """
        pass
