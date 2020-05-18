from datetime import datetime

file_date_format_string = '%Y_%m_%d_%H_%M_%S'
log_date_format_string = '%d-%m-%Y (%H:%M:%S)'


def get_datetime_now_file_string() -> str:
    """
    Returns datetime now formatted
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

    f = open("/sys/class/thermal/thermal_zone0/temp", "r")
    cpu = f.readline()
    values = {'Temperature (Chip)': str(int(cpu) / 1000) + ' \'C'}

    return values
