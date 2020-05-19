import os
import unittest
from os import listdir
from os.path import isfile
from time import sleep

import pytest

from src.camera.camera_base import CameraBase, CameraState, get_camera
from src.camera.camera_mock import Camera
from src.utils.observer import Observer
from src.utils.utils import is_raspbian

chunk_length = 3
test_recordings_path = './test_cameras'


class MockStreamingOutput(object):
    """
    The output for the camera web stream.
    """

    def __init__(self):
        """ Constructor s"""
        self.buf = b''

    def write(self, buf):
        """
        Write to the stream buffer.
        """
        self.buf = buf


class TestCameraFactory(unittest.TestCase):
    """
    Tests for the camera factory
    """

    def setUp(self) -> None:
        """ Setup """
        self.camera = get_camera(recordings_path=test_recordings_path)
        assert self.camera

    def test_get_camera(self):
        """
        Test: Create a camera on different platforms.
        """
        assert is_raspbian() is self.camera.is_real_camera()

    def test_singleton(self):
        """
        Test: Camera singleton pattern.
        """
        assert get_camera() == self.camera
        assert get_camera(chunk_length=14) == self.camera


class TestCameraBase(unittest.TestCase):
    """
    Tests for the camera interface.
    """

    def setUp(self) -> None:
        """ Setup """
        self.camera = CameraBase(chunk_length=75,
                                 recordings_path=test_recordings_path)

    def test_create_mock_camera(self):
        """
        Test: Constructor generates camera in correct state.
        """
        assert self.camera.camera_state == CameraState.OFF
        assert not self.camera.is_real_camera()
        assert self.camera.chunk_length == 75

    def test_set_camera_state(self):
        """
        Test: Camera state set correctly and observers notified.
        """
        observer = Observer()
        self.camera.attach(observer)

        assert observer.notification
        assert 'attached_to' in observer.notification
        assert observer.notification['attached_to'] == self.camera

        self.camera.set_camera_state(CameraState.IDLE)
        assert observer.notification['state'] == CameraState.IDLE

        self.camera.set_camera_state(CameraState.OFF)
        assert observer.notification['state'] == CameraState.OFF

        self.camera.set_camera_state(CameraState.STOPPING_RECORD)
        assert observer.notification['state'] == CameraState.STOPPING_RECORD

        self.camera.set_camera_state(CameraState.RECORDING)
        assert observer.notification['state'] == CameraState.RECORDING

    def test_start_stop_record_transition(self):
        """
        Test: Camera state transition working.
        """
        start_stop_transition(self.camera)

    def test_start_stop_record_transition_with_observer(self):
        """
        Test: Camera state transition working with observer.
        """
        start_stop_transition(self.camera, [Observer()])

    def test_streaming_allowed(self):
        """
        Test: Streaming allowed function does nothing on base
        """
        output = MockStreamingOutput()
        assert output.buf == b''
        self.camera.streaming_allowed(output)
        assert output.buf != b''


def start_stop_transition(camera, observers=[]):
    """
    Helper for the start stop transition.
    """
    assert camera.camera_state == CameraState.OFF
    for observer in observers:
        camera.attach(observer)

    with camera:
        assert camera.camera_state == CameraState.IDLE

        camera.start_recording()
        assert camera.camera_state == CameraState.RECORDING
        check_camera_state_in_observer(camera, CameraState.RECORDING)

        camera.stop_recording()
        assert camera.camera_state == CameraState.IDLE
        check_camera_state_in_observer(camera, CameraState.IDLE)

    assert camera.camera_state == CameraState.OFF
    check_camera_state_in_observer(camera, CameraState.OFF)


def check_camera_state_in_observer(camera, camera_state):
    """
    Helper to check if given state is in notifications of all observers.
    """
    for observer in camera.observers:
        assert 'state' in observer.notification
        assert observer.notification['state'] == camera_state


class TestCameraMock(unittest.TestCase):
    """
    Tests for the camera mock.
    """

    def setUp(self) -> None:
        """ Setup """
        self.camera = Camera(recordings_path=test_recordings_path)

    def test_record(self):
        """
        Test: Recording of the mock camera.
        """
        assert self.camera.camera_state == CameraState.OFF

        with self.camera:
            assert self.camera.camera_state == CameraState.IDLE

            self.camera.start_recording()

            assert self.camera.record_thread is not None
            sleep(3)
            assert self.camera.record_thread is not None

            self.camera.stop_recording()
            assert self.camera.record_thread is None


class TestCameraPi(unittest.TestCase):
    """
    Tests for the camera mock.
    """

    def setUp(self):
        """ Setup """
        self.camera = create_and_assert_physical_camera()

    def test_start_stop_camera(self):
        """
        Test: Start and stop of camera.
        """
        self.camera.start_camera()
        assert self.camera.real_camera
        assert self.camera.camera_state == CameraState.IDLE

        self.camera.stop_camera()
        assert not self.camera.real_camera
        assert self.camera.camera_state == CameraState.OFF

    def test_record(self):
        """
        Test: Recording of the physical camera.
        """
        with self.camera:
            assert self.camera.camera_state == CameraState.IDLE
            self.camera.start_recording()
            assert self.camera.camera_state == CameraState.RECORDING
            assert self.camera.recordings_folder.current_recordings_folder

            print(self.camera.recordings_folder.current_recordings_folder)

            for i in range(5):
                wait_and_assert_chunk_created(self.camera, i)

            self.camera.stop_recording()
            assert self.camera.record_thread is None

    def test_streaming_allowed(self):
        """
        Test: Streaming is allowed
        """
        output = MockStreamingOutput()
        with self.camera:
            self.camera.streaming_allowed(output)
            assert output.buf.startswith(b'\xff\xd8')


def create_and_assert_physical_camera():
    """
    Helper: Tries to create a physical camera.
    """
    camera = get_camera(chunk_length=chunk_length,
                        recordings_path=test_recordings_path)

    assert not camera.recordings_folder.current_recordings_folder
    assert camera.camera_state == CameraState.OFF
    assert camera.chunk_length is chunk_length

    if not camera.is_real_camera():
        pytest.skip("Camera can only be testes on raspbian.", )
        return None

    return camera


def wait_and_assert_chunk_created(camera, i):
    """
    Waits until chunk is finished and new one is created
    """
    assert camera.record_thread is not None
    sleep(chunk_length)
    recordings = \
        [f for f in
         listdir(
             camera.recordings_folder.current_recordings_folder)
         if isfile(os.path.join(
            camera.recordings_folder.current_recordings_folder,
            f))]
    print(recordings)
    assert len(recordings) == (i + 1)
    for recording in recordings:
        assert str(recording).endswith('.h264')


@pytest.fixture(autouse=True, scope='session')
def test_suite_before_and_after_all():
    """
    Before all and After all for the RecordingsFolder.
    """
    # setup
    yield
    # teardown - put your command here
    import shutil

    shutil.rmtree(test_recordings_path)
