import os
import shutil
import unittest
from pathlib import Path

from src.utils.recordings_folder import RecordingsFolder
from src.utils.utils import get_project_path

test_path_prefix = 'test_recordings_folder'
folder_names = ['', 'test_split_path_1',
                'test_split_path_2', 'test_split_path_3',
                'recordings/*']
tests_folders = [os.path.join(get_project_path(), test_path_prefix, f) for f in
                 folder_names]
base_path_string = ''
for f in tests_folders:
    base_path_string += f + ';'


class PathTestsBase(unittest.TestCase):
    """
    Base for the tests that need paths set up.
    """

    def setUp(self) -> None:
        """ Setup """
        self.paths = []
        for path in tests_folders:
            if path.endswith('*'):
                clean_path = path.replace('*', '')
                for p in ['a', 'b', 'c', 'd', 'e']:
                    join_path = os.path.join(clean_path, p)
                    self.paths.append(join_path)
                    Path(join_path).mkdir(parents=True, exist_ok=True)
            else:
                self.paths.append(path)

    def tearDown(self) -> None:
        """ Tear down """
        for path in self.paths:
            shutil.rmtree(path, ignore_errors=True)


class TestRecordingsFolder(PathTestsBase):
    """
    Tests for recordings_folder.py
    """

    def setUp(self) -> None:
        """ Setup """
        super().setUp()
        self.recordings_folder = RecordingsFolder(base_path_string)

    def test_path_splitting(self):
        """
        Test: Singleton class design of RecordingsFolder
        """
        for path in self.recordings_folder.base_paths:
            assert path in self.paths

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
            assert next_chunk_path.split('/')[-3] == test_path_prefix
            assert next_chunk_path.startswith(
                self.recordings_folder.current_recordings_folder)

            current_chunk_path = next_chunk_path

    def test_non_existing_paths_skipped(self):
        """
        Test: Non existing paths are not used for writing
        """
        non_existing_paths = '/nfjdksn/fdsfsd;/kdfjnsf;/mnt/;/opt/;'
        self.recordings_folder = RecordingsFolder(
            non_existing_paths + base_path_string)
        print(self.recordings_folder.base_paths)

        chunk_path = self.recordings_folder.get_next_chunk_path()
        assert chunk_path.startswith(self.paths[0])

        chunk_path = self.recordings_folder.get_next_chunk_path()
        assert chunk_path.startswith(self.paths[0])
