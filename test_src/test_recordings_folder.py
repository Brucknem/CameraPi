import os
import shutil
import unittest

from src.utils.recordings_folder import RecordingsFolder

tests_folder = './test_recordings_folder'


class TestRecordingsFolder(unittest.TestCase):
    """
    Tests for recordings_folder.py
    """

    def setUp(self) -> None:
        """ Setup """
        self.recordings_folder = RecordingsFolder(tests_folder)

    def tearDown(self) -> None:
        """ Tear down """
        shutil.rmtree(tests_folder)

    def test_can_write_to_dir(self):
        """
        Test: Can not write to permission denied dir.
        """
        assert RecordingsFolder(
            '/mnt/test_camerapi/').base_path == './recordings'

    def test_module_constructor(self):
        """
        Test: Singleton class design of RecordingsFolder
        """

        assert self.recordings_folder.base_path == tests_folder
        test_base_path = os.path.join(tests_folder, 'test_module_constructor')

        assert self.recordings_folder is not RecordingsFolder(test_base_path)
        assert os.path.exists(self.recordings_folder.base_path)
        assert os.path.exists(self.recordings_folder.log_dir)

    def test_base_path(self):
        """
        Tests the base path setting and path creation
        """
        assert self.recordings_folder.base_path
        assert self.recordings_folder.datetime_now
        assert self.recordings_folder.log_dir
        assert self.recordings_folder.log_file_path
        assert not self.recordings_folder.current_recordings_folder
        assert os.path.exists(self.recordings_folder.base_path)
        assert os.path.exists(self.recordings_folder.log_dir)

    def test_create_new_recording(self):
        """
        Test: Create a new folder for recordings.
        """

        for i in range(5):
            current_recordings_folder = \
                self.recordings_folder.current_recordings_folder
            print('Current recordings folder: ', current_recordings_folder)

            self.recordings_folder.create_new_recording()

            assert self.recordings_folder.current_recordings_folder is not None

            new_recordings_folder = \
                self.recordings_folder.current_recordings_folder
            print('New recordings folder: ', new_recordings_folder)

            assert current_recordings_folder is not new_recordings_folder
            assert os.path.exists(new_recordings_folder)

    def test_get_next_chunk_path(self):
        """
        Tests: Return the full path to the current chunk.
        """
        current_chunk_path = self.recordings_folder.get_next_chunk_path()

        for i in range(5):
            print('Current chunk path: ', current_chunk_path)

            next_chunk_path = self.recordings_folder.get_next_chunk_path()
            print('Next chunk path: ', next_chunk_path)

            assert next_chunk_path is not current_chunk_path

            assert next_chunk_path.endswith('.h264')
            assert next_chunk_path.startswith(tests_folder)
            assert next_chunk_path.startswith(
                self.recordings_folder.current_recordings_folder)

            current_chunk_path = next_chunk_path
