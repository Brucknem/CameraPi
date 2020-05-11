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

            RecordingsFolder.__instance.datetime_now = datetime.now()
            RecordingsFolder.__instance.log_dir = \
                os.path.join(base_path, get_datetime_now_file_string())
            Path(RecordingsFolder.__instance.log_dir).mkdir(parents=True,
                                                            exist_ok=True)
            RecordingsFolder.__instance.log_file_path = os.path.join(
                RecordingsFolder.__instance.log_dir, 'log.txt')
        return RecordingsFolder.__instance
