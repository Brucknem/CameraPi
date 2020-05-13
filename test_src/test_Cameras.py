import os
from os import listdir
from os.path import isfile
from time import sleep

import pytest

from src.RecordingsFolder import RecordingsFolder
from src.camera.CameraMock import CameraMock
from src.camera.ICamera import ICamera, CameraState, create_camera

tests_folder = './test_cameras'
recordings_folder = RecordingsFolder(tests_folder)


class TestICamera:
    """
    Tests for the camera interface.
    """

    def test_create_mock_camera(self):
        """
        Test: Constructor generates camera in correct state.
        """
        mock_camera = ICamera(chunk_length=75)
        assert mock_camera.camera_state == CameraState.IDLE
        assert not mock_camera.is_real_camera()
        assert mock_camera.chunk_length == 75

    def test_set_camera_state(self):
        """
        Test: Camera state transition working.
        """
        mock_camera = ICamera()
        assert mock_camera.camera_state == CameraState.IDLE

        mock_camera.start_recording()
        assert mock_camera.camera_state == CameraState.RECORDING

        mock_camera.stop_recording()
        assert mock_camera.camera_state == CameraState.IDLE


class TestCameraMock:
    """
    Tests for the camera mock.
    """

    def test_record(self):
        """
        Test: Start and stop recording on the mock camera.
        """
        mock_camera = CameraMock()
        assert mock_camera.camera_state == CameraState.IDLE

        mock_camera.start_recording()

        assert mock_camera.record_thread is not None
        sleep(3)
        assert mock_camera.record_thread is not None

        mock_camera.stop_recording()
        assert mock_camera.record_thread is None


class TestCamera:
    """
    Tests for the camera mock.
    """

    def test_record(self):
        """
        Test: Start and stop recording on the mock camera.
        """
        camera = create_camera()
        if not camera.is_real_camera():
            pytest.skip("Camera can only be testes on raspbian.")
            return

        assert recordings_folder.current_recordings_folder is None

        chunk_length = 3
        assert camera.camera_state == CameraState.IDLE
        assert camera.chunk_length is chunk_length

        camera.start_recording()

        print(recordings_folder.current_recordings_folder)

        for i in range(5):
            assert camera.record_thread is not None
            sleep(chunk_length)
            recordings = \
                [f for f in
                 listdir(recordings_folder.current_recordings_folder)
                 if isfile(os.path.join(
                    str(recordings_folder.current_recordings_folder), f))]
            print(recordings)
            assert len(recordings) == (i + 1)
            for recording in recordings:
                assert str(recording).endswith('.h264')

        camera.stop_recording()
        assert camera.record_thread is None


@pytest.fixture(autouse=True, scope='session')
def test_suite_before_and_after_all():
    """
    Before all and After all for the RecordingsFolder.
    """
    # setup
    yield
    # teardown - put your command here
    import shutil

    shutil.rmtree(tests_folder)
