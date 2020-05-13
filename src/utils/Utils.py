import inspect
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


def function_name(stack_depth: int = 1) -> str:
    """
    Returns the function name.

    :param stack_depth:
    :return:
    """
    return str(inspect.stack()[stack_depth][3])
