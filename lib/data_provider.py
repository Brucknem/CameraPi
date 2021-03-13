import pathlib


def get_data_path():
    return pathlib.Path(pathlib.Path(__file__).absolute().parent.parent, 'misc')
