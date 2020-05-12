import os

import pytest

from RecordingsFolder import RecordingsFolder

tests_folder = './tests'


class TestRecordingsFolder:
    """
    Tests for RecordingsFolder.py
    """

    def test_singleton(self):
        """
        Test: Singleton class design of RecordingsFolder
        """
        recordings_folder = RecordingsFolder(tests_folder)

        assert recordings_folder.base_path == tests_folder

        assert recordings_folder is RecordingsFolder()
        assert recordings_folder is RecordingsFolder('./otherTest')
        assert recordings_folder.log_dir is RecordingsFolder(
            './otherTest').log_dir
        assert recordings_folder.log_file_path is RecordingsFolder(
            './otherTest').log_file_path
        assert recordings_folder.current_recordings_folder is RecordingsFolder(
            './otherTest').current_recordings_folder

    def test_create_new_recording(self):
        """
        Test: Create a new folder for recordings.
        """

        assert RecordingsFolder().current_recordings_folder is None

        for i in range(5):
            current_recordings_folder = \
                RecordingsFolder().current_recordings_folder
            print('Current recordings folder: ', current_recordings_folder)

            RecordingsFolder(tests_folder).create_new_recording()

            assert RecordingsFolder().current_recordings_folder is not None

            new_recordings_folder = \
                RecordingsFolder().current_recordings_folder
            print('New recordings folder: ', new_recordings_folder)

            assert current_recordings_folder is not new_recordings_folder
            assert os.path.exists(new_recordings_folder)

    def test_get_next_chunk_path(self):
        """
        Tests: Return the full path to the current chunk.
        """
        current_chunk_path = RecordingsFolder().get_next_chunk_path()

        for i in range(5):
            print('Current chunk path: ', current_chunk_path)

            next_chunk_path = RecordingsFolder().get_next_chunk_path()
            print('Next chunk path: ', next_chunk_path)

            assert next_chunk_path is not current_chunk_path

            assert next_chunk_path.endswith('.h264')
            assert next_chunk_path.startswith(tests_folder)
            assert next_chunk_path.startswith(
                RecordingsFolder().current_recordings_folder)

            current_chunk_path = next_chunk_path


@pytest.fixture(autouse=True, scope='session')
def test_suite_before_and_after_all():
    """
    Before all and After all for the RecordingsFolder.
    """
    # setup
    RecordingsFolder(tests_folder)
    yield
    # teardown - put your command here
    import shutil

    shutil.rmtree(tests_folder)
