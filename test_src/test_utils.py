from pathlib import Path

from src.utils.utils import read_ip
from src.utils.utils import split_path_list
from test_src.test_recordings_folder import tests_folders, base_path_string, \
    PathTestsBase


class TestUtils(PathTestsBase):
    """
    Tests for the utils
    """

    def setUp(self) -> None:
        """ Setup """
        super().setUp()
        for path in self.paths:
            Path(path).mkdir(parents=True,
                             exist_ok=True)

    def test_read_ip(self):
        """
        Test: Read ip
        """
        ip = read_ip()
        assert ip

    def test_split_path_list(self):
        """
        Test: Split the base path list
        """

        path_list = split_path_list(base_path_string)
        for path in path_list:
            assert path in self.paths

    def test_split_path_single(self):
        """
        Test: Split the base path list
        """
        paths_raw = tests_folders[0]
        path_list = split_path_list(paths_raw)

        assert path_list == [tests_folders[0], ]

    def test_split_path_empty(self):
        """"
        Test: Empty path split correct
        """
        assert [] == split_path_list('')

    def test_single_with_glob(self):
        """"
        Test: Empty path split correct
        """
        paths = split_path_list(tests_folders[4])
        for path in paths:
            assert path.split('/')[-1] in ['a', 'b', 'c', 'd', 'e']
