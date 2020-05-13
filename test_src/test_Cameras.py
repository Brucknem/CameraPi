import os
from os import listdir
from os.path import isfile
from time import sleep

import pytest

from src.camera.CameraBase import CameraBase, CameraState, get_camera
from src.camera.MockCamera import MockCamera
from src.utils.Utils import is_raspbian

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
        Test: Camera state transition working.
        """
        camera = CameraBase()
        assert camera.camera_state == CameraState.OFF

        with camera:
            assert camera.camera_state == CameraState.IDLE

            camera.start_recording()
            assert camera.camera_state == CameraState.RECORDING

            camera.stop_recording()
            assert camera.camera_state == CameraState.IDLE

        assert camera.camera_state == CameraState.OFF


class TestMockCamera:
    """
    Tests for the camera mock.
    """

    def test_record(self):
        """
        Test: Start and stop recording on the mock camera.
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


class TestPhysicalCamera:
    """
    Tests for the camera mock.
    """

    def test_record(self):
        """
        Test: Start and stop recording on the mock camera.
        """
        chunk_length = 3
        camera = get_camera(chunk_length=chunk_length,
                            recordings_path=test_recordings_path)

        assert not camera.recordings_folder.current_recordings_folder
        assert camera.camera_state == CameraState.OFF
        assert camera.chunk_length is chunk_length

        if not camera.is_real_camera():
            pytest.skip("Camera can only be testes on raspbian.", )
            return

        with camera:
            assert camera.camera_state == CameraState.IDLE
            camera.start_recording()
            assert camera.camera_state == CameraState.RECORDING
            assert camera.recordings_folder.current_recordings_folder

            print(camera.recordings_folder.current_recordings_folder)

            for i in range(5):
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

    shutil.rmtree(test_recordings_path)


if __name__ == '__main__':
    TestPhysicalCamera().test_record()
