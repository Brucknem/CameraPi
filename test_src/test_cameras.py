import os
import unittest
from os import listdir
from os.path import isfile
from time import sleep

import pytest

from src.camera.camera_base import CameraBase, get_camera
from src.camera.camera_pi import Camera
from src.camera.camera_state import CameraState
from src.utils.Observer import Observer
from src.utils.Utils import is_raspbian

chunk_length = 3
test_recordings_path = './test_cameras'


class TestCameraSingletonPattern(unittest.TestCase):
    """
    Tests for the camera singleton pattern
    """

    def setUp(self):
        """ Setup """
        self.camera = get_camera(recordings_path=test_recordings_path)
        assert self.camera

    def test_singleton(self):
        """
        Test: Create a camera on different platforms
        """
        assert is_raspbian() is self.camera.is_real_camera()
        camera_copies = [get_camera(recordings_path=test_recordings_path) for
                         i in range(5)]
        for camera_copy_a in camera_copies:
            for camera_copy_b in camera_copies:
                assert camera_copy_a is camera_copy_b

    def tearDown(self):
        """ Tear down """
        self.camera = None


class TestCameraBase(unittest.TestCase):
    """
    Tests for the camera interface.
    """

    def test_create_mock_camera(self):
        """
        Test: Constructor generates camera in correct state.
        """
        mock_camera = CameraBase(chunk_length=75)
        assert mock_camera.camera_state == CameraState.IDLE
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

    def test_exception_on_frames(self):
        """
        Test: frames() raises exception
        """
        with self.assertRaises(RuntimeError):
            CameraBase().frames()


def start_stop_transition(camera, observers=[]):
    """
    Helper for the start stop transition.
    """
    assert camera.camera_state == CameraState.IDLE
    for observer in observers:
        camera.attach(observer)

    with camera:
        assert camera.camera_state == CameraState.RECORDING
        check_camera_state_in_observer(camera, CameraState.RECORDING)

    assert camera.camera_state == CameraState.IDLE
    check_camera_state_in_observer(camera, CameraState.IDLE)


def check_camera_state_in_observer(camera, camera_state):
    """
    Helper to check if given state is in notifications of all observers.
    """
    for observer in camera.observers:
        assert 'state' in observer.notification
        assert observer.notification['state'] == camera_state


class TestCameraImageStream(unittest.TestCase):
    """
    Tests for the camera mock.
    """

    def setUp(self):
        """ Setup """
        from src.camera.camera_image_stream import Camera
        self.camera = Camera()
        assert self.camera.camera_state == CameraState.IDLE

    def test_record(self):
        """
        Test: Recording of the mock camera.
        """

        with self.camera:
            assert self.camera.camera_state == CameraState.RECORDING
            assert self.camera.record_thread is not None
            sleep(3)
            assert self.camera.record_thread is not None

        assert self.camera.record_thread is None

    def check_correct_frame_stream(self):
        """
        Helper: Check if the mock camera images are from the stream.
        """
        from src.camera.camera_image_stream import Camera
        stream_mock_files = Camera.get_default_images()

        for i in range(5):
            frame = self.camera.get_frame()
            if frame not in stream_mock_files:
                return False
        return True

    def test_stream_returns_correct_frames(self):
        """
        Test: Stream correct giving frames.
        """
        assert self.check_correct_frame_stream()

    def test_start_stop_streaming(self):
        """
        Test: Start and stop of camera streaming.
        """

        assert self.camera.allow_streaming
        assert self.check_correct_frame_stream()

        self.camera.allow_streaming = False
        assert not self.camera.allow_streaming
        assert not self.check_correct_frame_stream()

        assert self.camera.get_frame() == CameraBase.default_image

        self.camera.allow_streaming = True
        assert self.camera.allow_streaming
        assert self.check_correct_frame_stream()
        assert self.camera.get_frame() != CameraBase.default_image

    def tearDown(self):
        """ Tear down """
        self.camera = None


class TestCameraPi(unittest.TestCase):
    """
    Tests for the camera mock.
    """

    def setUp(self):
        """ Setup """
        self.camera = create_and_assert_physical_camera()

    def test_start(self):
        """
        Test: Start and stop of camera.
        """
        assert self.camera.pi_camera
        assert self.camera.camera_state == CameraState.IDLE

    def test_record(self):
        """
        Test: Recording of the physical camera.
        """
        with self.camera:
            assert self.camera.camera_state == CameraState.RECORDING
            assert self.camera.recordings_folder.current_recordings_folder

            print(self.camera.recordings_folder.current_recordings_folder)

            for i in range(5):
                wait_and_assert_chunk_created(self.camera, i)

        assert self.camera.record_thread is None

    def test_stream_returns_correct_frames(self):
        """
        Test: Stream correct giving frames.
        """

        for i in range(10):
            frame = self.camera.get_frame()
            assert is_jpg(frame)
            yield None

    def test_start_stop_streaming(self):
        """
        Test: Start and stop of camera streaming.
        """

        assert self.camera.allow_streaming
        frame = self.camera.get_frame()
        assert frame != CameraBase.default_image
        # assert is_jpg(frame)

        self.camera.allow_streaming = False
        frame = self.camera.get_frame()
        assert frame == CameraBase.default_image
        # assert is_jpg(frame)

        self.camera.allow_streaming = True
        frame = self.camera.get_frame()
        assert frame != CameraBase.default_image
        # assert is_jpg(frame)

    def test_destructor(self):
        """
        Test: Destructor working
        """
        assert self.camera
        del self.camera

    def tearDown(self):
        """ Tear down """
        self.camera = None


def create_and_assert_physical_camera() -> Camera or None:
    """
    Helper: Tries to create a physical camera.
    """
    camera = get_camera(chunk_length=chunk_length,
                        recordings_path=test_recordings_path)

    assert not camera.recordings_folder.current_recordings_folder
    assert camera.camera_state == CameraState.IDLE
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


def is_jpg(image_data):
    """
    Helper: Is the given image_data valid JPEG
    """
    try:
        from PIL import Image
        image = Image.frombytes('RGB', (1200, 900), image_data, 'raw')
        return image.format == 'JPEG'
    except IOError:
        return False


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
