import os
from datetime import datetime
from pathlib import Path

from Utils import get_datetime_now_file_string


class RecordingsFolder(object):
    """
    Wrapper that holds all necessary file paths for logging and recording.
    """
    __instance = None

    def __new__(cls, base_path: str = './recordings/'):
        """
        Singleton constructor.
        """
        if RecordingsFolder.__instance is None:
            RecordingsFolder.__instance = object.__new__(cls)

            RecordingsFolder.__instance.base_path = base_path

            RecordingsFolder.__instance.datetime_now = datetime.now()
            RecordingsFolder.__instance.log_dir = \
                os.path.join(base_path, get_datetime_now_file_string())
            Path(RecordingsFolder.__instance.log_dir).mkdir(parents=True,
                                                            exist_ok=True)
            RecordingsFolder.__instance.log_file_path = os.path.join(
                RecordingsFolder.__instance.log_dir, 'log.txt')
            RecordingsFolder.__instance.current_recordings_folder = None
        return RecordingsFolder.__instance

    def create_new_recording(self):
        """
        Creates a new folder for recordings.
        """
        self.current_recordings_folder = os.path.join(
            self.log_dir,
            get_datetime_now_file_string())
        Path(self.current_recordings_folder).mkdir(
            parents=True, exist_ok=True)

    def get_next_chunk_path(self):
        """
        Returns the full path to the current chunk.
        :return:
        """
        return os.path.join(self.current_recordings_folder,
                            get_datetime_now_file_string() + '.h264')
