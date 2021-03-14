import os
import socket
from datetime import datetime
from os.path import dirname
from pathlib import Path

TEMPERATURE_CHIP_KEY = 'Temperature (Chip)'

file_date_format_string = '%Y_%m_%d_%H_%M_%S'
log_date_format_string = '%Y-%m-%d %H:%M:%S'


def get_default_recordings_path() -> str:
    """
    Returns the default recordings path
    """
    return os.path.join(dirname(dirname(__file__)), 'recordings/')


def get_datetime_now_file_string() -> str:
    """
    Returns datetime now formatted for filename
    """
    return datetime.now().strftime(file_date_format_string)


def get_datetime_now_log_string() -> str:
    """
    Returns datetime now formatted
    """
    return datetime.now().strftime(log_date_format_string)


def is_raspbian():
    """
    Checks if the platform is a raspbian device
    """
    with open('/proc/cpuinfo', 'r') as cpuinfo:
        import re
        if len(re.findall(r"ARMv\d Processor", cpuinfo.read())) > 0:
            return True
        else:
            return False


def read_cpu_temperature():
    """
    Read the pressure, temperature and humidity from the sense hat and log.
    """

    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        cpu = f.readline()
        values = {
            TEMPERATURE_CHIP_KEY: str(round(int(cpu) / 1000, 2)) + ' \'C'}

    return values


def read_file_relative_to(filename: str, relative_to: str,
                          decode: bool = False):
    """
    Reads a file relative to another file.
    """
    with open(
            os.path.join(dirname(os.path.abspath(relative_to)), filename),
            'rb') as f:
        file = f.read()

        if not decode:
            return file
        else:
            return file.decode("utf-8")


last_cached_ip = None


def read_ip():
    """
    Reads the own ip.
    """
    global last_cached_ip
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        last_cached_ip = ip
    except Exception:
        pass
    return last_cached_ip


def can_write_to_dir(base_path):
    """
    Checks if the base dir can be written.
    """
    try:
        Path(base_path).mkdir(parents=True, exist_ok=True)

        if not os.path.exists(base_path):
            return False
        test_file_path = os.path.join(base_path,
                                      'write_access_test_file')
        with open(test_file_path, 'w') as file:
            file.write('assert can write')
        if not os.path.exists(test_file_path):
            return False
        with open(test_file_path, 'r') as file:
            if not file.read() == 'assert can write':
                return False
        os.remove(test_file_path)
        return True
    except Exception:
        return False


def split_path_list(path_list_string: str):
    """
    Splits the given path list into its paths
    """
    if not path_list_string:
        return []

    if ';' in path_list_string:
        path_list = path_list_string.split(';')
    else:
        path_list = [path_list_string, ]

    path_list = [p for p in path_list if p]
    path_list = [expand_glob(p) for p in path_list]
    path_list = [item for sublist in path_list for item in sublist]
    return path_list


def expand_glob(path: str):
    """
    Expands a * glob
    """
    if not path.endswith('*'):
        return [path, ]

    path = path.replace('*', '')
    try:
        paths = [os.path.join(path, x) for x in os.listdir(path)]
        return paths
    except FileNotFoundError:
        return [path, ]


def get_project_path():
    """
    Returns the path to the src files
    """
    return dirname(dirname(get_default_recordings_path()))
