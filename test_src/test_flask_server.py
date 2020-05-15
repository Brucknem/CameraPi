import os
import shutil
from multiprocessing import Process
from time import sleep
from unittest import TestCase

from selenium import webdriver

from src.camera.camera_base import get_camera
from src.utils.Utils import is_raspbian
from src.web.flask_server import FlaskAppWrapper

chunk_length = 3
test_flask_server_path = 'test_flask_server'

flask_app_wrapper = FlaskAppWrapper(get_camera())


class TestFlaskServer(TestCase):
    """
    Tests for the flask ui server
    """

    def setUp(self) -> None:
        """ Setup"""
        path = '/usr/local/bin/'
        if is_raspbian():
            path = '/usr/lib/chromium-browser/'
        self.driver = webdriver.Chrome(os.path.join(path, 'chromedriver'))

        self.server = Process(target=flask_app_wrapper.run)
        self.server.start()
        sleep(3)

    def tearDown(self):
        """
        Tear down web streaming and driver.
        """
        self.driver.close()

        self.server.terminate()
        self.server.join()

        shutil.rmtree(test_flask_server_path, ignore_errors=True)

    def test_open_web_streaming(self):
        """
        Test: Page is opened correct.
        """
        self.driver.get('http://0.0.0.0:5000')
        assert 'Camera Pi' in self.driver.title

    def test_recording(self):
        """
        Test: Page is opened correct.
        """
        self.driver.get('http://0.0.0.0:5000')
        assert 'Camera Pi' in self.driver.title

        self.click_start()
        assert 'start' in self.extract_get_values()

        self.click_stop()
        assert 'stop' in self.extract_get_values()

    def assert_start_stop_recording(self, start, stop):
        """
        Asserts the given button setting.
        """
        assert self.get_start_recording().is_enabled() == start
        assert self.get_stop_recording().is_enabled() == stop

    def get_start_recording(self):
        """
        Checks if the start button is enabled.
        """
        start_recording = self.driver.find_element_by_name('start')
        assert start_recording.is_enabled
        return start_recording

    def get_stop_recording(self):
        """
        Checks if the start button is enabled.
        """
        stop_recording = self.driver.find_element_by_name('stop')
        assert stop_recording.is_enabled
        return stop_recording

    def click_start(self):
        """
        Clicks on the start button.
        """
        self.assert_start_stop_recording(True, False)
        start_recording = self.get_start_recording()
        start_recording.click()
        self.assert_start_stop_recording(False, True)

    def click_stop(self):
        """
        Clicks on the stop button.
        """
        stop_recording = self.get_stop_recording()
        stop_recording.click()
        self.assert_start_stop_recording(True, False)

    def extract_get_values(self):
        """
        Helper: Extracts a dict of the url get values.
        """

        parse_url = self.driver.current_url

        if '?' not in parse_url:
            return {}

        raw_values = parse_url.split('?')[1]
        if '=' not in raw_values:
            return {}

        values = {}
        raw_values = raw_values.split('=')

        for i in range(0, len(raw_values), 2):
            values[raw_values[i]] = raw_values[i + 1]

        return values
