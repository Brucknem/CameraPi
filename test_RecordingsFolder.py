import pytest

from RecordingsFolder import RecordingsFolder

tests_folder = './tests'
recordingsFolder = RecordingsFolder(tests_folder)


class TestRecordingsFolder:
    """
    Tests for RecordingsFolder.py
    """

    def test_singleton(self):
        """
        Test: Singleton class design of RecordingsFolder
        """
        recordingsfolder = RecordingsFolder(tests_folder)

        assert recordingsfolder.base_path == tests_folder

        assert recordingsfolder is RecordingsFolder()
        assert recordingsfolder is RecordingsFolder('./otherTest')
        assert recordingsfolder.log_dir is RecordingsFolder(
            './otherTest').log_dir
        assert recordingsfolder.log_file_path is RecordingsFolder(
            './otherTest').log_file_path
        assert recordingsfolder.current_recordings_folder is RecordingsFolder(
            './otherTest').current_recordings_folder

    def test_create_new_recording(self):
        """
        Test: Create a new folder for recordings.
        """
        RecordingsFolder(tests_folder).create_new_recording()

        assert RecordingsFolder().current_recordings_folder is not None

    def get_next_chunk_path(self):
        """
        Tests: Return the full path to the current chunk.
        """
        pass


# content of conftest.py or a tests file (e.g. in your tests or root directory)

@pytest.fixture(autouse=True, scope='session')
def test_suite_cleanup_thing():
    """
    Cleanup for the tests folder.
    """
    # setup
    yield
    # teardown - put your command here
    import shutil

    shutil.rmtree(tests_folder)
