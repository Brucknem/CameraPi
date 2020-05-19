import os
from datetime import datetime
from pathlib import Path

from src.utils.utils import get_datetime_now_file_string, \
    assert_can_write_to_dir


class RecordingsFolder:
    """
    Wrapper that holds all necessary file paths for logging and recording.
    """

    def __init__(self, base_path: str = './recordings/'):
        """ constructor """
        self.base_path: str = ''
        self.datetime_now: datetime = datetime.now()
        self.log_dir: str = ''
        self.log_file_path: os.path = os.path.join(base_path)
        self.current_recordings_folder: str = ''
        self.set_base_path(base_path)

    def set_base_path(self, base_path):
        """
        Sets the base path and setups the necessary followup paths.
        """
        try:
            if not assert_can_write_to_dir(base_path):
                base_path = './recordings'
            self.base_path: str = base_path
            self.datetime_now: datetime = datetime.now()
            self.current_recordings_folder: str = ''
            self.log_dir = os.path.join(base_path,
                                        get_datetime_now_file_string())
            Path(self.log_dir).mkdir(parents=True, exist_ok=True)
            self.log_file_path = os.path.join(self.log_dir, 'log.txt')
        except Exception:
            self.set_base_path('./recordings')

    def create_new_recording(self):
        """
        Creates a new folder for recordings.
        """
        self.current_recordings_folder = os.path.join(
            self.log_dir, get_datetime_now_file_string())
        Path(self.current_recordings_folder).mkdir(parents=True, exist_ok=True)

    def get_next_chunk_path(self):
        """
        Returns the full path to the current chunk.
        :return:
        """
        if not self.current_recordings_folder:
            self.create_new_recording()
        return os.path.join(self.current_recordings_folder,
                            get_datetime_now_file_string() + '.h264')
