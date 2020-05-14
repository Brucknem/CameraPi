from src.utils.Observable import Observable
from src.utils.Observer import Observer


def create_observable_observer_combination(num_observables, num_observers):
    """
    Creates a given number ob observables and observers
    """
    observables = [Observable() for i in range(num_observables)]
    observers = [Observer() for i in range(num_observers)]

    for observable in observables:
        for observer in observers:
            observable.attach(observer)
            assert observer in observable.observers

    return observables, observers


class TestObserverPattern:
    """
    Tests for the observer pattern
    """

    def test_attach_detach(self):
        """
        Test: Attach and detach an observer.
        """
        observable, observer = create_observable_observer_combination(1, 1)
        observable = observable[0]
        observer = observer[0]

        assert observer in observable.observers
        assert observer.notification
        assert 'attached_to' in observer.notification
        assert observer.notification['attached_to'] is observable

        observable.detach(observer)
        assert observer not in observable.observers
        assert observer.notification
        assert 'detached_from' in observer.notification
        assert observer.notification['detached_from'] is observable

    def test_notify(self):
        """
        Test: Notify observers.
        """
        observables, observers = create_observable_observer_combination(1, 1)
        test_notifications = [
            {'a': True},
            {'a': True, 'b': 'received'},
            {'a': True, 'b': 'received', 'state': 'idle'},
        ]

        for test_notification in test_notifications:
            for observable in observables:
                observable.notify(**test_notification, observable=observable)
                for observer in observers:
                    assert observer.notification == \
                           dict(**test_notification, observable=observable)
