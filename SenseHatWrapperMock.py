from ISenseHatWrapper import ISenseHatWrapper


class SenseHatWrapperMock(ISenseHatWrapper):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
        from sense_emu import SenseHat
        self.sense = SenseHat()
