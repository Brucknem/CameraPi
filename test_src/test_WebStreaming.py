# import logging
# import unittest
# from threading import Thread
#
# from selenium.webdriver.common.keys import Keys
#
# from src.web.WebStreaming import get_web_streaming
#
# enter = Keys.RETURN
#
# chunk_length = 3
# test_recordings_path = './test_webstreaming'
#
# web_streaming_is_running = True
#
#
# def setup_camera_and_web_streaming():
#     """
#     Helper: Starts a thread with a running web streaming server
#     """
#     thread = Thread(target=web_streaming_thread, args=())
#     thread.daemon = True
#     thread.start()
#
#
# def web_streaming_thread():
#     """
#     Helper: The web streaming thread.
#     """
#     global web_streaming_is_running
#     web_streaming_is_running = True
#
#     logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
#                         level=logging.INFO)
#     logging.info('Started monitoring')
#
#     camera = get_camera(chunk_length, test_recordings_path)
#     web_streaming = get_web_streaming()
#
#     with camera:
#         web_streaming.set_camera(camera)
#         camera.attach(web_streaming)
#
#         while web_streaming_is_running:
#             pass
#
#     web_streaming.stop_streaming()
#
#
# class TestWebStreaming(unittest.TestCase):
#     """
#     UI Tests for the web streaming.
#     """
#     pass
#     # def setUp(self):
#     #     """
#     #     Set up web streaming and driver.
#     #     """
#     #     setup_camera_and_web_streaming()
#     #     path = '/usr/local/bin'
#     #     if is_raspbian():
#     #         path = '/usr/lib/chromium-browser/'
#     #     self.driver = webdriver.Chrome(os.path.join(path, 'chromedriver'))
#     #
#     # def test_open_web_streaming(self):
#     #     """
#     #     Test: Page is opened correct.
#     #     """
#     #     self.driver.get('http://localhost:8080')
#     #     assert 'Camera Pi' in self.driver.title
#     #
#     # def test_recording(self):
#     #     """
#     #     Test: Page is opened correct.
#     #     """
#     #     self.driver.get('http://localhost:8080')
#     #     assert 'Camera Pi' in self.driver.title
#     #
#     #     self.click_start()
#     #     assert 'start' in self.extract_get_values()
#     #
#     #     self.click_stop()
#     #     assert 'stop' in self.extract_get_values()
#     #
#     # def assert_start_stop_recording(self, start, stop):
#     #     """
#     #     Asserts the given button setting.
#     #     """
#     #     assert self.get_start_recording().is_enabled() == start
#     #     assert self.get_stop_recording().is_enabled() == stop
#     #
#     # def get_start_recording(self):
#     #     """
#     #     Checks if the start button is enabled.
#     #     """
#     #     start_recording = self.driver.find_element_by_name('start')
#     #     assert start_recording.is_enabled
#     #     return start_recording
#     #
#     # def get_stop_recording(self):
#     #     """
#     #     Checks if the start button is enabled.
#     #     """
#     #     stop_recording = self.driver.find_element_by_name('stop')
#     #     assert stop_recording.is_enabled
#     #     return stop_recording
#     #
#     # def click_start(self):
#     #     """
#     #     Clicks on the start button.
#     #     """
#     #     self.assert_start_stop_recording(True, False)
#     #     start_recording = self.get_start_recording()
#     #     start_recording.click()
#     #     self.assert_start_stop_recording(False, True)
#     #
#     # def click_stop(self):
#     #     """
#     #     Clicks on the stop button.
#     #     """
#     #     stop_recording = self.get_stop_recording()
#     #     stop_recording.click()
#     #     self.assert_start_stop_recording(True, False)
#     #
#     # def tearDown(self):
#     #     """
#     #     Tear down web streaming and driver.
#     #     """
#     #     global web_streaming_is_running
#     #     web_streaming_is_running = False
#     #     self.driver.close()
#     #     shutil.rmtree(test_recordings_path)
#     #
#     # def extract_get_values(self):
#     #     """
#     #     Helper: Extracts a dict of the url get values.
#     #     """
#     #
#     #     parse_url = self.driver.current_url
#     #
#     #     if '?' not in parse_url:
#     #         return {}
#     #
#     #     raw_values = parse_url.split('?')[1]
#     #     if '=' not in raw_values:
#     #         return {}
#     #
#     #     values = {}
#     #     raw_values = raw_values.split('=')
#     #
#     #     for i in range(0, len(raw_values), 2):
#     #         values[raw_values[i]] = raw_values[i + 1]
#     #
#     #     return values
