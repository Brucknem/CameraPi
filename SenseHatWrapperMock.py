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

    def read_sensors(self):
        """ Override """

        f = open("/sys/class/thermal/thermal_zone0/temp", "r")
        cpu = f.readline()
        return {'Temperature (Chip)': str(int(cpu) / 1000) + ' \'C'}
