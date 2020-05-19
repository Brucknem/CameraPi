import shutil
import unittest
from time import sleep

import numpy as np
import pytest

from src.camera.camera_base import get_camera, CameraBase
from src.camera.camera_state import CameraState
from src.sense_hat_wrapper.sense_hat_wrapper import TEMPERATURE_PRESSURE_KEY, \
    TEMPERATURE_HUMIDITY_KEY, PRESSURE, HUMIDITY
from src.sense_hat_wrapper.sense_hat_wrapper_base import SenseHatWrapperBase, \
    camera_state_to_color_map, get_sense_hat
from src.utils.utils import TEMPERATURE_CHIP_KEY, is_raspbian

chunk_length = 3
tests_folder = './test_sense_hat_folder'
max_sense_hat_difference = list((1, 1, 1))


class ReleaseEvent:
    """
    Mock event for the joystick callbacks
    """

    def __init__(self):
        """ Constructor """
        self.action = 'released'


class PressedEvent:
    """
    Mock event for the joystick callbacks
    """

    def __init__(self):
        """ Constructor """
        self.action = 'pressed'


class TestSenseHatWrapperBase(unittest.TestCase):
    """
    Tests for the sense hat wrapper base.
    """

    def setUp(self) -> None:
        """ Setup """
        self.camera = get_camera(chunk_length, tests_folder)
        self.sense_hat = SenseHatWrapperBase(self.camera, message='')

    def test_get_sense_hat(self):
        """
        Test: Get sense hat function.
        """
        sense_hat = get_sense_hat(self.camera, 'test')
        assert sense_hat.is_real_sense_hat() == is_raspbian()

    def test_display_camera_state(self):
        """
        Test: Set the sense hat matrix.
        """
        for state in CameraState:
            set_and_assert_display_state(self.sense_hat, state)

    def tearDown(self) -> None:
        """ Tear down """
        del self.camera
        del self.sense_hat
        shutil.rmtree(tests_folder)

    def test_show_ip(self):
        """
        Test: Show ip
        """
        assert self.sense_hat.show_ip()

    def test_update(self):
        """
        Test: Update method
        """
        for state in CameraState:
            set_and_assert_camera_state(self.camera, self.sense_hat, state)

    def test_read_sensors(self):
        """
        Test: Temperature (Chip) correct read as sense hat value
        """
        values = self.sense_hat.read_sensors()
        assert values


class TestSenseHatWrapper(TestSenseHatWrapperBase):
    """
    Tests for the sense hat wrapper.
    """

    def setUp(self) -> None:
        """ Setup """
        self.camera = get_camera(chunk_length, tests_folder)
        self.sense_hat = get_sense_hat(self.camera, message='')
        if not self.sense_hat.is_real_sense_hat():
            pytest.skip('Not on raspbian or no sense hat connected.')
        assert self.sense_hat in self.camera.observers

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

    def test_clear(self):
        """
        Test: Clear the matrix:
        """
        self.sense_hat.clear()

    def test_update(self):
        """
        Test: Update method
        """
        assert_sense_hat_matrix_color(self.sense_hat,
                                      camera_state_to_color_map[
                                          CameraState.OFF])

        with self.camera:
            sleep(2)
            assert_sense_hat_matrix_color(self.sense_hat,
                                          camera_state_to_color_map[
                                              CameraState.IDLE])

            self.camera.start_recording()
            sleep(2)
            assert_sense_hat_matrix_color(self.sense_hat,
                                          camera_state_to_color_map[
                                              CameraState.RECORDING])

            self.camera.stop_recording()
            sleep(2)
            assert_sense_hat_matrix_color(self.sense_hat,
                                          camera_state_to_color_map[
                                              CameraState.IDLE])
        sleep(2)
        assert_sense_hat_matrix_color(self.sense_hat,
                                      camera_state_to_color_map[
                                          CameraState.OFF])

    def test_start_stop_recording(self):
        """
        Test: Start the camera.
        """
        assert self.camera.camera_state == CameraState.OFF

        with self.camera:
            sleep(2)
            assert self.camera.camera_state == CameraState.IDLE

            self.sense_hat.start_recording(ReleaseEvent())
            sleep(2)
            assert self.camera.camera_state == CameraState.RECORDING

            self.sense_hat.stop_recording(ReleaseEvent())
            sleep(2)
            assert self.camera.camera_state == CameraState.IDLE

        sleep(2)
        assert self.camera.camera_state == CameraState.OFF


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
