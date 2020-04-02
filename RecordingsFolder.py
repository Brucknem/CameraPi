import os
from pathlib import Path

from Utils import *


class RecordingsFolder:
    """
    Wrapper that holds all necessary file paths for logging and recording.
    """

    def __init__(self, base_path: str = '/mnt/harddrive/recordings/nightsight/'):
        """
        Constructor.
        """
        self.datetime_now = datetime.now()
        self.log_dir = os.path.join(base_path, get_datetime_now_file_string())
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        self.log_file_path = os.path.join(self.log_dir, 'log.txt')
        self.write_to_log('RecordingsFolder', 'Started monitoring')

    def write_to_log(self, function_name: str, key: any, value: any = None):
        """
        Write to log file.

        :param function_name:
        :param key: The key message that is written.
        :param value: An optional value
        """
        try:
            with open(self.log_file_path, 'a+') as file:
                output_string: str = '[' + get_datetime_now_log_string() + ']\t'

                output_string += function_name + ':\t'
                output_string += str(key)
                if value:
                    output_string += ':\t' + str(value)

                output_string += '\n'
                print(output_string)
                file.write(output_string)
        except Exception as err:
            print(err)

    # def remove_all_logs(self, event):
    #     """
    #     Removes all log files.
    #     (Joystick key callback)
    #
    #     :param event: the key input event
    #     """
    #     if event.action == 'released':
    #         return
    #
    #     try:
    #         for filename in os.listdir(self.log_dir):
    #             if filename == self.log_file_name:
    #                 continue
    #             file_path = os.path.join(self.log_dir, filename)
    #             try:
    #                 if os.path.isfile(file_path) or os.path.islink(file_path):
    #                     os.unlink(file_path)
    #                 elif os.path.isdir(file_path):
    #                     shutil.rmtree(file_path)
    #             except Exception as e:
    #                 self.write_to_log('Failed to delete %s: %s' % (file_path, e))
    #     except Exception as err:
    #         self.write_to_log(err)
