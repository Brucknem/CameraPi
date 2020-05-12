from os import listdir
from os.path import isfile, join
from time import sleep

import pytest

from CameraMock import CameraMock
from ICamera import ICamera, CameraState
from RecordingsFolder import RecordingsFolder


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
        try:
            from Camera import Camera
        except Exception:
            pytest.skip("Camera can only be testes on raspbian.")
            return

        assert RecordingsFolder().current_recordings_folder is None

        chunk_length = 3
        mock_camera = Camera(chunk_length)
        assert mock_camera.camera_state == CameraState.IDLE
        assert mock_camera.chunk_length is chunk_length

        mock_camera.start_recording()

        print(RecordingsFolder().current_recordings_folder)

        for i in range(5):
            assert mock_camera.record_thread is not None
            sleep(chunk_length)
            recordings = [f for f in
                          listdir(RecordingsFolder().current_recordings_folder)
                          if isfile(join(RecordingsFolder().
                                         current_recordings_folder, f))]
            print(recordings)
            assert len(recordings) == (i + 1)
            for recording in recordings:
                assert str(recording).endswith('.h264')

        mock_camera.stop_recording()
        assert mock_camera.record_thread is None


if __name__ == '__main__':
    TestCameraMock().test_record()
