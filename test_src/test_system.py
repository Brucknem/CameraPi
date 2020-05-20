import os
from os import listdir
from os.path import isfile, join
from time import sleep

import pytest

from src.sense_hat_wrapper.sense_hat_wrapper import SenseHatWrapper
from src.sense_hat_wrapper.sense_hat_wrapper_base import get_sense_hat
from src.utils.utils import is_raspbian
from test_src.test_sense_hat_wrapper import \
    assert_sense_hat_matrix_color_by_state, ReleaseEvent
from test_src.test_web_streaming import TestViewBase
from test_src.test_web_streaming import index_url, settings_url

chunk_length = 3
test_recordings_path = './test_system'


class TestSystem(TestViewBase):
    """
    UI Tests for the web streaming.
    """

    def setUp(self):
        """ Setup """
        if not is_raspbian():
            pytest.skip('Not on raspbian or no sense hat connected.')
        super().setUp()

    def create_sense_hat(self):
        """
        Creates a sense hat using the camera.
        """
        return get_sense_hat(self.camera)

    def test_start_stop_recording(self):
        """
        Test: One whole iteration through all functions.
        """
        with self.camera:
            self.create_web_streaming()
            sense_hat = self.create_sense_hat()

            self.driver.get(index_url)
            assert self.driver.current_url == index_url

            self.driver.get(settings_url)
            assert self.driver.current_url == settings_url
            self.assert_start_stop_recording(True, False)

            self.start_stop_by_ui(sense_hat)
            self.start_stop_by_sense_hat(sense_hat)
            self.start_by_ui_stop_by_sense_hat(sense_hat)
            self.start_by_sense_hat_stop_by_ui(sense_hat)

    def assert_recording_written(self):
        """
        Helper: Asserts recordings is written
        """
        sleep(2)
        path = self.camera.recordings_folder.current_recordings_folder
        assert os.path.exists(path)
        possible_recordings = [f for f in listdir(path) if
                               isfile(join(path, f))]
        assert possible_recordings
        assert possible_recordings[0].endswith('.h264')

    def start_stop_by_ui(self, sense_hat):
        """
        Test: Start stop by ui
        """
        self.start_by_ui(sense_hat)
        self.stop_by_ui(sense_hat)

    def start_by_ui(self, sense_hat):
        """
        Helper: Start recording by ui
        """
        self.click_start()
        self.assert_start_stop_recording(False, True)
        assert_sense_hat_matrix_color_by_state(sense_hat,
                                               self.camera.camera_state)
        assert self.camera.is_recording()
        self.assert_recording_written()

    def start_stop_by_sense_hat(self, sense_hat: SenseHatWrapper):
        """
        Test: Start stop by sense_hat
        """
        self.start_by_sense_hat(sense_hat)
        self.stop_by_sense_hat(sense_hat)

    def start_by_sense_hat(self, sense_hat):
        """
        Helper: Start recording by sense hat
        """
        sense_hat.start_recording(ReleaseEvent())
        sleep(1)
        self.assert_start_stop_recording(False, True)
        assert_sense_hat_matrix_color_by_state(sense_hat,
                                               self.camera.camera_state)
        assert self.camera.is_recording()
        self.assert_recording_written()

    def start_by_ui_stop_by_sense_hat(self, sense_hat: SenseHatWrapper):
        """
        Test: Start stop by sense_hat
        """
        self.start_by_ui(sense_hat)
        self.stop_by_sense_hat(sense_hat)

    def stop_by_sense_hat(self, sense_hat):
        """
        Helper: Stop recording by sense hat
        """
        sense_hat.stop_recording(ReleaseEvent())
        sleep(1)
        self.assert_start_stop_recording(True, False)
        assert_sense_hat_matrix_color_by_state(sense_hat,
                                               self.camera.camera_state)
        assert not self.camera.is_recording()

    def start_by_sense_hat_stop_by_ui(self, sense_hat: SenseHatWrapper):
        """
        Test: Start stop by sense_hat
        """
        self.start_by_sense_hat(sense_hat)
        self.stop_by_ui(sense_hat)

    def stop_by_ui(self, sense_hat):
        """
        Helper: Stop recording by ui
        """
        self.click_stop()
        self.assert_start_stop_recording(True, False)
        assert_sense_hat_matrix_color_by_state(sense_hat,
                                               self.camera.camera_state)
        assert not self.camera.is_recording()
