from src.utils import Observer


class Observable:
    """
    Observable (Observer pattern)
    """

    def __init__(self):
        """
        Constructor.
        """
        self.observers: list[Observer] = []

    def attach(self, observer: Observer):
        """
        Attaches an observer
        """
        self.observers.append(observer)

    def detach(self, observer: Observer):
        """
        Detaches an observer
        """
        self.observers.remove(observer)

    def notify(self, **kwargs):
        """
        Notifies all observers
        """
        for observer in self.observers:
            observer.update(**kwargs)
