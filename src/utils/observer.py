class Observer:
    """
    Observer (Observer pattern)
    """

    def __init__(self):
        """
        Constructor.
        """
        self.notification = None

    def update(self, **kwargs):
        """
        Observer update.
        """
        self.notification = kwargs
