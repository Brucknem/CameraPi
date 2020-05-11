from time import sleep

import pytest

from CameraMock import CameraMock
from ICamera import ICamera, CameraState
from RecordingsFolder import RecordingsFolder

tests_folder = './tests'
recordingsFolder = RecordingsFolder(tests_folder)


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
        assert mock_camera.chunk_length is 75

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

    def test_get_chunk_path(self):
        """
        Test: Formatting of the chunk path.
        """
        mock_camera = ICamera()

        print(mock_camera.get_chunk_path())
        assert str.startswith(mock_camera.get_chunk_path(), './tests')
        assert len(mock_camera.get_chunk_path().split('/')) is 4
        assert str.endswith(mock_camera.get_chunk_path(), '.h264')


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
        try:
            from Camera import Camera
        except:
            pytest.skip("Camera can only be testes on raspbian.")
            return

        mock_camera = Camera()
        assert mock_camera.camera_state == CameraState.IDLE

        mock_camera.start_recording()

        assert mock_camera.record_thread is not None
        sleep(3)
        assert mock_camera.record_thread is not None

        mock_camera.stop_recording()
        assert mock_camera.record_thread is None


if __name__ is '__main__':
    TestCameraMock().test_record()


@pytest.yield_fixture(autouse=True, scope='session')
def test_suite_cleanup_thing():
    # setup
    yield
    # teardown - put your command here
    import shutil

    shutil.rmtree(tests_folder)
