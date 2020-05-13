from src.sense_hat.ISenseHatWrapper import ISenseHatWrapper


class SenseHatWrapperMock(ISenseHatWrapper):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self):
        """
        Constructor.
        """
        from sense_emu import SenseHat
        super().__init__(SenseHat())
