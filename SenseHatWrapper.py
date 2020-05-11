from ISenseHatWrapper import ISenseHatWrapper


class SenseHatWrapper(ISenseHatWrapper):
    """
    Wrapper for the Sense Hat functions.
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
        from sense_hat import SenseHat
        self.sense = SenseHat()
