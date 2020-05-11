from Camera import CameraState
from Observer import Observer
from ISenseHatWrapper import ISenseHatWrapper


class SenseHatWrapperMock(Observer, ISenseHatWrapper):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
