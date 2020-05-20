import unittest

from src.utils.utils import read_ip


class TestUtils(unittest.TestCase):
    """
    Tests for the utils
    """

    def test_read_ip(self):
        """
        Test: Read ip
        """
        ip = read_ip()
        assert ip
