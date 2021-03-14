import os
from datetime import datetime
from pathlib import Path

from lib.utils import get_datetime_now_file_string, \
    can_write_to_dir, get_default_recordings_path, split_path_list


class RecordingsFolder:
    """
    Wrapper that holds all necessary file paths for logging and recording.
    """

    def __init__(self, base_path_list: str = get_default_recordings_path()):
        """ constructor """
        self.datetime_now: datetime = datetime.now()
        self.base_paths: list = split_path_list(base_path_list)
        self.log_dir: str = ''
        self.current_recordings_folder: str = ''

    def create_new_recording(self):
        """
        Creates a new folder for recordings.
        """
        if not self.log_dir or not can_write_to_dir(self.log_dir):
            for path in self.base_paths:
                if can_write_to_dir(path):
                    self.log_dir = path
                    break

        if not self.log_dir:
            self.log_dir = get_default_recordings_path()

        self.current_recordings_folder = \
            os.path.join(self.log_dir, get_datetime_now_file_string())

        Path(self.current_recordings_folder).mkdir(parents=True,
                                                   exist_ok=True)

    def get_next_chunk_path(self):
        """
        Returns the full path to the current chunk.
        :return:
        """
        if not self.current_recordings_folder:
            self.create_new_recording()
        return os.path.join(self.current_recordings_folder,
                            get_datetime_now_file_string() + '.h264')
