import logging
import os
import shutil
import unittest
from threading import Thread
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from src.camera.camera_base import get_camera
from src.utils.utils import is_raspbian
from src.web.web_streaming import get_web_streaming

base_url = 'http://0.0.0.0:8080/index.html'

enter = Keys.RETURN

chunk_length = 3
test_recordings_path = './test_webstreaming'

web_streaming_is_running = False


def setup_camera_and_web_streaming():
    """
    Helper: Starts a thread with a running web streaming server
    """
    thread = Thread(target=web_streaming_thread, args=())
    thread.daemon = True
    thread.start()


def web_streaming_thread():
    """
    Helper: The web streaming thread.
    """
    global web_streaming_is_running
    web_streaming_is_running = True

    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                        level=logging.INFO)
    logging.info('Started monitoring')

    camera = get_camera(chunk_length, test_recordings_path)

    with camera:
        web_streaming = get_web_streaming(camera)
        camera.attach(web_streaming)

        while web_streaming_is_running:
            pass


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


class TestWebStreaming(unittest.TestCase):
    """
    UI Tests for the web streaming.
    """

    def setUp(self):
        """
        Set up web streaming and driver.
        """
        path = '/usr/local/bin'
        if is_raspbian():
            path = '/usr/lib/chromium-browser/'
        self.driver = webdriver.Chrome(os.path.join(path, 'chromedriver'))
        self.camera = get_camera(chunk_length, test_recordings_path)

    def test_start_stop_streaming(self):
        """
        Tests if server is really not reachable if streaming is stopped.
        """

        with self.camera:
            self.camera.streaming_chunk_length = 1
            web_streaming = get_web_streaming(self.camera)
            self.assert_correct_camera_view_shown()

            web_streaming.camera.is_output_allowed = False
            sleep(2)
            self.driver.get(base_url)
            assert 'Camera Pi' in self.driver.title
            size = self.driver.find_element_by_id('stream_image').size
            assert (size['height'] - size['width'] / 2) < 3

            assert not get_start_recording(self.driver).is_enabled()
            assert not get_stop_recording(self.driver).is_enabled()

            web_streaming.camera.is_output_allowed = True
            self.assert_correct_camera_view_shown()

    def assert_correct_camera_view_shown(self):
        """
        Asserts that the image stream is the correct image.
        """
        self.driver.get(base_url)
        assert 'Camera Pi' in self.driver.title
        size = self.driver.find_element_by_id('stream_image').size
        if self.camera.is_real_camera():
            assert (size['height'] - size['width'] / 2) > 3
        else:
            assert (size['height'] - size['width'] / 2) < 3

    def tearDown(self):
        """
        Tear down web streaming and driver.
        """
        sleep(2)
        self.driver.close()
        shutil.rmtree(test_recordings_path)


class TestUI(unittest.TestCase):
    """
    UI Tests for the web streaming.
    """

    def setUp(self):
        """
        Set up web streaming and driver.
        """
        path = '/usr/local/bin'
        if is_raspbian():
            path = '/usr/lib/chromium-browser/'
        self.driver = webdriver.Chrome(os.path.join(path, 'chromedriver'))
        setup_camera_and_web_streaming()

    def tearDown(self):
        """
        Tear down web streaming and driver.
        """
        sleep(2)
        self.driver.close()
        shutil.rmtree(test_recordings_path)
        global web_streaming_is_running
        web_streaming_is_running = False
        sleep(2)

    def test_open_web_streaming(self):
        """
        Test: Page is opened correct.
        """
        self.driver.get(base_url)
        assert 'Camera Pi' in self.driver.title

    def test_recording(self):
        """
        Test: Page is opened correct.
        """
        self.driver.get(base_url)
        assert 'Camera Pi' in self.driver.title

        self.click_start()
        assert 'start' in self.extract_get_values()

        self.click_stop()
        assert 'stop' in self.extract_get_values()

    def assert_start_stop_recording(self, start, stop):
        """
        Asserts the given button setting.
        """
        assert get_start_recording(self.driver).is_enabled() == start
        assert get_stop_recording(self.driver).is_enabled() == stop

    def click_start(self):
        """
        Clicks on the start button.
        """
        self.assert_start_stop_recording(True, False)
        start_recording = get_start_recording(self.driver)
        start_recording.click()
        self.assert_start_stop_recording(False, True)

    def click_stop(self):
        """
        Clicks on the stop button.
        """
        stop_recording = get_stop_recording(self.driver)
        stop_recording.click()
        sleep(2)
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


def get_start_recording(driver):
    """
    Checks if the start button is enabled.
    """
    start_recording = driver.find_element_by_name('start')
    return start_recording


def get_stop_recording(driver):
    """
    Checks if the start button is enabled.
    """
    stop_recording = driver.find_element_by_name('stop')
    return stop_recording
