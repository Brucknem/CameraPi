import os
import shutil
import unittest
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from src.camera.camera_base import get_camera
from src.utils.utils import is_raspbian, get_project_path
from src.web.web_streaming import get_web_streaming, toggle_allow_streaming_url

index_url = 'http://0.0.0.0:8080/index.html'
settings_url = 'http://0.0.0.0:8080/settings.html'
allow_streaming_url = 'http://0.0.0.0:8080' + toggle_allow_streaming_url

chunk_length = 3
test_recordings_path = os.path.join(get_project_path(), 'test_webstreaming')


def curl(url):
    """
    Helper: Returns the curl result if host responds else None.
    """
    import pycurl
    from io import BytesIO

    b_obj = BytesIO()
    crl = pycurl.Curl()

    # Set URL value
    crl.setopt(crl.URL, url)
    crl.setopt(pycurl.TIMEOUT, 1)

    # Write bytes that are utf-8 encoded
    crl.setopt(crl.WRITEDATA, b_obj)

    try:
        # Perform a file transfer
        crl.perform()

        # Get the content stored in the BytesIO object (in byte characters)
        get_body = b_obj.getvalue()

        # Decode the bytes stored in get_body to HTML and print the result
        output = get_body.decode('utf8')

        print('Output of GET request:\n%s' % output)
        return output
    except Exception:
        return None
    finally:
        # End curl session
        crl.close()


class TestViewBase(unittest.TestCase):
    """
    UI Tests for the web streaming.
    """

    def setUp(self):
        """
        Set up web streaming and driver.
        """
        self.start_web_driver()
        self.camera = get_camera(chunk_length, test_recordings_path)

    def tearDown(self):
        """
        Tear down web streaming and driver.
        """
        self.driver.close()
        shutil.rmtree(test_recordings_path, ignore_errors=True)

    def start_web_driver(self):
        """
        Starts the web driver.
        """
        path = '/usr/local/bin'
        if is_raspbian():
            path = '/usr/lib/chromium-browser/'
        self.driver = webdriver.Chrome(os.path.join(path, 'chromedriver'))

    def create_web_streaming(self):
        """
        Creates a web streaming object using the camera
        """
        self.camera.streaming_chunk_length = 1
        web_streaming = get_web_streaming(self.camera)
        self.assert_correct_camera_view_shown(index_url)
        return web_streaming

    def assert_correct_camera_view_shown(self, url, is_output_allowed=True):
        """
        Asserts that the image stream is the correct image.
        """
        self.driver.get(url)
        assert 'Camera Pi' in self.driver.title
        size = self.driver.find_element_by_id('stream_image').size
        if is_output_allowed and self.camera.is_real_camera():
            assert (size['height'] - size['width'] / 2) > 3
        else:
            assert (size['height'] - size['width'] / 2) < 3

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

    def assert_start_stop_recording(self, start, stop):
        """
        Asserts the given button setting.
        """
        assert self.get_element_by_name('start').is_enabled() == start
        assert self.get_element_by_name('stop').is_enabled() == stop

    def get_element_by_name(self, name):
        """
        Gets an ui element by its name
        """
        try:
            start_recording = self.driver.find_element_by_name(name)
            return start_recording
        except NoSuchElementException:
            return None

    def click_start(self):
        """
        Clicks on the start button.
        """
        self.assert_start_stop_recording(True, False)
        start_recording = self.get_element_by_name('start')
        start_recording.click()
        self.assert_start_stop_recording(False, True)

    def click_stop(self):
        """
        Clicks on the stop button.
        """
        stop_recording = self.get_element_by_name('stop')
        stop_recording.click()
        self.assert_start_stop_recording(True, False)


class TestIndexView(TestViewBase):
    """
    UI Tests for the web streaming.
    """

    def test_open_web_streaming(self):
        """
        Test: Page is opened correct.
        """
        with self.camera:
            self.create_web_streaming()
            self.driver.get(index_url)
            assert 'Camera Pi' in self.driver.title
            assert not self.get_element_by_name('start')
            assert not self.get_element_by_name('stop')


class TestSettingsView(TestViewBase):
    """
    UI Tests for the web streaming.
    """

    def test_start_stop_streaming(self):
        """
        Tests if server is really not reachable if streaming is stopped.
        """

        with self.camera:
            web_streaming = self.create_web_streaming()
            self.assert_correct_camera_view_shown(index_url)
            self.assert_correct_camera_view_shown(settings_url)

            self.driver.get(settings_url)
            assert 'Camera Pi' in self.driver.title
            assert self.driver.current_url == settings_url

            web_streaming.camera.is_output_allowed = False
            assert not self.camera.is_output_allowed

            self.driver.get(settings_url)
            assert 'Camera Pi' in self.driver.title
            assert self.driver.current_url == index_url
            assert not self.get_element_by_name('start')
            assert not self.get_element_by_name('stop')
            self.assert_correct_camera_view_shown(index_url, False)
            self.assert_correct_camera_view_shown(settings_url, False)

            web_streaming.camera.is_output_allowed = True
            assert self.camera.is_output_allowed
            assert web_streaming.camera.is_output_allowed

            self.driver.get(settings_url)
            assert 'Camera Pi' in self.driver.title
            assert self.driver.current_url == settings_url
            assert self.get_element_by_name('start')
            assert self.get_element_by_name('stop')
            self.assert_correct_camera_view_shown(index_url)
            self.assert_correct_camera_view_shown(settings_url)

    def test_recording(self):
        """
        Test: Page is opened correct.
        """

        with self.camera:
            self.create_web_streaming()
            self.driver.get(settings_url)
            assert 'Camera Pi' in self.driver.title
            assert not self.camera.is_recording()
            self.assert_start_stop_recording(True, False)

            self.click_start()
            assert self.camera.is_recording()
            self.assert_start_stop_recording(False, True)

            self.click_stop()
            assert not self.camera.is_recording()
            self.assert_start_stop_recording(True, False)


class TestToggleAllowStreaming(TestViewBase):
    """
    Tests the toggle allow
    """

    def test_toggle_allow_streaming(self):
        """
        Test: Allow and disallow streaming
        """
        with self.camera:
            self.create_web_streaming()

            assert self.camera.is_output_allowed
            self.assert_correct_camera_view_shown(index_url)
            self.assert_correct_camera_view_shown(settings_url)

            self.driver.get(allow_streaming_url)
            assert not self.camera.is_output_allowed
            assert self.driver.current_url == index_url
            self.assert_correct_camera_view_shown(index_url, False)
            self.assert_correct_camera_view_shown(settings_url, False)

            self.driver.get(allow_streaming_url)
            assert self.camera.is_output_allowed
            assert self.driver.current_url == index_url
            self.assert_correct_camera_view_shown(index_url)
            self.assert_correct_camera_view_shown(settings_url)


class TestJavaScript(TestViewBase):
    """
    Tests the javascript events.
    """

    def test_measurements_update(self):
        """
        Test: Measurements get updated every 3 seconds.
        """
        with self.camera:
            self.create_web_streaming()
            self.driver.get(index_url)

            old_measurements = self.driver.find_element_by_id(
                'measurements').get_attribute('innerHTML')

            for _ in range(3):
                sleep(4)
                new_measurements = self.driver.find_element_by_id(
                    'measurements').get_attribute('innerHTML')
                assert old_measurements != new_measurements
                old_measurements = new_measurements

    def test_buttons_correct_enabled(self):
        """
        Test: Buttons correct enabled on start and stop recording.
        """
        with self.camera:
            self.create_web_streaming()
            self.driver.get(settings_url)
            self.assert_start_stop_recording(True, False)

            self.camera.start_recording()
            sleep(1)
            self.assert_start_stop_recording(False, True)

            self.camera.stop_recording()
            sleep(1)
            self.assert_start_stop_recording(True, False)

    def test_redirect_on_streaming_not_allowed(self):
        """
        Test: Redirect when camera is not allowed to stream.
        """
        with self.camera:
            self.create_web_streaming()
            self.driver.get(settings_url)

            self.camera.is_output_allowed = False
            sleep(1)
            assert self.driver.current_url == index_url

            self.camera.is_output_allowed = True
            self.driver.get(settings_url)
            assert self.driver.current_url == settings_url
