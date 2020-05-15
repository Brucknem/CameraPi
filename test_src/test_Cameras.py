import os
import unittest
from os import listdir
from os.path import isfile
from time import sleep

import pytest

from src.WebStreaming import StreamingOutput
from src.camera.CameraBase import CameraBase, CameraState, get_camera
from src.camera.MockCamera import MockCamera
from src.utils.Observer import Observer
from src.utils.Utils import is_raspbian

chunk_length = 3
test_recordings_path = './test_cameras'


class TestCameraFactory:
    """
    Tests for the camera factory
    """

    def test_get_camera(self):
        """
        Test: Create a camera on different platforms
        """
        camera = get_camera(recordings_path=test_recordings_path)
        assert camera
        assert is_raspbian() is camera.is_real_camera()


class TestCameraBase:
    """
    Tests for the camera interface.
    """

    def test_create_mock_camera(self):
        """
        Test: Constructor generates camera in correct state.
        """
        mock_camera = CameraBase(chunk_length=75)
        assert mock_camera.camera_state == CameraState.OFF
        assert not mock_camera.is_real_camera()
        assert mock_camera.chunk_length == 75

    def test_set_camera_state(self):
        """
        Test: Camera state set correctly and observers notified.
        """
        camera = CameraBase()
        observer = Observer()
        camera.attach(observer)

        assert observer.notification
        assert 'attached_to' in observer.notification
        assert observer.notification['attached_to'] == camera

        camera.set_camera_state(CameraState.IDLE)
        assert observer.notification['state'] == CameraState.IDLE

        camera.set_camera_state(CameraState.OFF)
        assert observer.notification['state'] == CameraState.OFF

        camera.set_camera_state(CameraState.STOPPING_RECORD)
        assert observer.notification['state'] == CameraState.STOPPING_RECORD

        camera.set_camera_state(CameraState.RECORDING)
        assert observer.notification['state'] == CameraState.RECORDING

    def test_start_stop_record_transition(self):
        """
        Test: Camera state transition working.
        """
        start_stop_transition(CameraBase())

    def test_start_stop_record_transition_with_observer(self):
        """
        Test: Camera state transition working with observer.
        """
        start_stop_transition(CameraBase(), [Observer()])


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


class TestMockCamera:
    """
    Tests for the camera mock.
    """

    def test_record(self):
        """
        Test: Recording of the mock camera.
        """
        mock_camera = MockCamera()
        assert mock_camera.camera_state == CameraState.OFF

        with mock_camera:
            assert mock_camera.camera_state == CameraState.IDLE

            mock_camera.start_recording()

            assert mock_camera.record_thread is not None
            sleep(3)
            assert mock_camera.record_thread is not None

            mock_camera.stop_recording()
            assert mock_camera.record_thread is None


class TestPhysicalCamera(unittest.TestCase):
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

    def test_start_stop_streaming(self):
        """
        Test: Start and stop of camera streaming.
        """
        with self.camera:
            assert self.camera.camera_state == CameraState.IDLE
            output = StreamingOutput()
            assert self.camera.start_streaming(output)
            assert self.camera.output

            self.camera.stop_streaming()
            assert not self.camera.output


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
