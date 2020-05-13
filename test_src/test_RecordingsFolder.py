import os

import pytest

from src.RecordingsFolder import RecordingsFolder

tests_folder = './test_recordings_folder'
recordings_folder = RecordingsFolder(tests_folder)


class TestRecordingsFolder:
    """
    Tests for RecordingsFolder.py
    """

    def test_module_constructor(self):
        """
        Test: Singleton class design of RecordingsFolder
        """

        assert recordings_folder.base_path == tests_folder
        test_base_path = os.path.join(tests_folder, 'test_module_constructor')

        assert recordings_folder is not RecordingsFolder(test_base_path)
        assert os.path.exists(recordings_folder.base_path)
        assert os.path.exists(recordings_folder.log_dir)

    def test_base_path(self):
        """
        Tests the base path setting and path creation
        """
        test_base_path = os.path.join(tests_folder, 'test_base_path')
        test_recordings_folder = RecordingsFolder(test_base_path)
        assert test_recordings_folder.base_path
        assert test_recordings_folder.datetime_now
        assert test_recordings_folder.log_dir
        assert test_recordings_folder.log_file_path
        assert not test_recordings_folder.current_recordings_folder
        assert os.path.exists(test_base_path)
        assert os.path.exists(test_recordings_folder.log_dir)

    def test_create_new_recording(self):
        """
        Test: Create a new folder for recordings.
        """

        for i in range(5):
            current_recordings_folder = \
                recordings_folder.current_recordings_folder
            print('Current recordings folder: ', current_recordings_folder)

            recordings_folder.create_new_recording()

            assert recordings_folder.current_recordings_folder is not None

            new_recordings_folder = \
                recordings_folder.current_recordings_folder
            print('New recordings folder: ', new_recordings_folder)

            assert current_recordings_folder is not new_recordings_folder
            assert os.path.exists(new_recordings_folder)

    def test_get_next_chunk_path(self):
        """
        Tests: Return the full path to the current chunk.
        """
        current_chunk_path = recordings_folder.get_next_chunk_path()

        for i in range(5):
            print('Current chunk path: ', current_chunk_path)

            next_chunk_path = recordings_folder.get_next_chunk_path()
            print('Next chunk path: ', next_chunk_path)

            assert next_chunk_path is not current_chunk_path

            assert next_chunk_path.endswith('.h264')
            assert next_chunk_path.startswith(tests_folder)
            assert next_chunk_path.startswith(
                recordings_folder.current_recordings_folder)

            current_chunk_path = next_chunk_path


@pytest.fixture(autouse=True, scope='session')
def test_recordings_folder_before_and_after_all():
    """
    Before all and After all for the RecordingsFolder.
    """
    # setup
    yield
    # teardown - put your command here
    import shutil

    shutil.rmtree(tests_folder)
