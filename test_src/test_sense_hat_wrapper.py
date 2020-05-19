import shutil
import unittest

import numpy as np
import pytest

from src.camera.camera_base import get_camera, CameraBase
from src.camera.camera_state import CameraState
from src.sense_hat_wrapper.sense_hat_wrapper import TEMPERATURE_PRESSURE_KEY, \
    TEMPERATURE_HUMIDITY_KEY, PRESSURE, HUMIDITY
from src.sense_hat_wrapper.sense_hat_wrapper_base import SenseHatWrapperBase, \
    camera_state_to_color_map, get_sense_hat
from src.utils.utils import TEMPERATURE_CHIP_KEY

chunk_length = 3
tests_folder = './test_sense_hat_folder'
max_sense_hat_difference = list((1, 1, 1))


class TestSenseHatWrapperBase(unittest.TestCase):
    """
    Tests for the sense hat wrapper base.
    """

    def setUp(self) -> None:
        """ Setup """
        self.camera = get_camera(chunk_length, tests_folder)
        self.sense_hat = get_sense_hat(self.camera, message='')

    def test_display_camera_state(self):
        """
        Test: Set the sense hat matrix.
        """
        for state in CameraState:
            set_and_assert_display_state(self.sense_hat, state)

    def test_clear(self):
        """
        Test: Clear the matrix:
        """
        self.sense_hat.clear()


class TestSenseHatWrapper(TestSenseHatWrapperBase):
    """
    Tests for the sense hat wrapper.
    """

    def setUp(self) -> None:
        """ Setup """
        self.camera = get_camera(chunk_length, tests_folder)
        try:
            from src.sense_hat_wrapper.sense_hat_wrapper import SenseHatWrapper
            self.sense_hat = SenseHatWrapper(self.camera, message='')
        except Exception:
            pytest.skip('Not on raspbian or no sense hat connected.')
        assert self.sense_hat.is_real_sense_hat()

    def tearDown(self) -> None:
        """ Tear down """
        del self.camera
        del self.sense_hat
        shutil.rmtree(tests_folder)

    def test_read_sensors(self):
        """
        Test: Temperature (Chip) correct read as sense hat value
        """
        values = self.sense_hat.read_sensors()
        assert values
        assert TEMPERATURE_CHIP_KEY in values
        assert TEMPERATURE_PRESSURE_KEY in values
        assert TEMPERATURE_HUMIDITY_KEY in values
        assert PRESSURE in values
        assert HUMIDITY in values

    def test_update(self):
        """
        Test: Update method
        """
        for state in CameraState:
            set_and_assert_camera_state(self.camera, self.sense_hat, state)


class TestSenseHatWrapperMock(TestSenseHatWrapperBase):
    """
    Tests for the sense hat wrapper mock.
    """

    def setUp(self) -> None:
        """ Setup """
        self.camera = get_camera(chunk_length, tests_folder)
        from src.sense_hat_wrapper.sense_hat_wrapper_mock import \
            SenseHatWrapperMock
        self.sense_hat = SenseHatWrapperMock(self.camera, message='')
        assert not self.sense_hat.is_real_sense_hat()

    def tearDown(self) -> None:
        """ Tear down """
        del self.camera
        del self.sense_hat
        shutil.rmtree(tests_folder)

    def test_read_sensors(self):
        """
        Test: Temperature (Chip) correct read as sense hat value
        """
        values = self.sense_hat.read_sensors()
        assert values
        assert TEMPERATURE_CHIP_KEY in values

    def test_update(self):
        """
        Test: Update method
        """
        for state in CameraState:
            set_and_assert_camera_state(self.camera, self.sense_hat, state)


def assert_sense_hat_matrix_color(sense_hat: SenseHatWrapperBase, color):
    """
    Helper: Asserts that the matrix is uniform colored.
    """
    for pixel in sense_hat.get_matrix():
        difference = np.abs(np.array(np.array(pixel) - np.array(color)))
        for i in range(len(difference)):
            assert difference[i] <= max_sense_hat_difference[i]


def set_and_assert_display_state(sense_hat: SenseHatWrapperBase,
                                 camera_state: CameraState):
    """
    Helper: Sets and asserts that the matrix is set correct.
    """
    sense_hat.display_camera_state(camera_state)
    assert_sense_hat_matrix_color(sense_hat,
                                  camera_state_to_color_map[
                                      camera_state])


def set_and_assert_camera_state(camera: CameraBase,
                                sense_hat: SenseHatWrapperBase,
                                camera_state: CameraState):
    """
    Helper: Sets the camera state and asserts that the matrix is set
    correct via the observer pattern.
    """
    camera.set_camera_state(camera_state)
    assert_sense_hat_matrix_color(sense_hat,
                                  camera_state_to_color_map[
                                      camera_state])
