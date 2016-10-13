# -*- coding: utf-8 -*-
import unittest
# from unittest.mock import MagicMock, patch


class TestGps(unittest.TestCase):

    def test_gps(self):
        pass


def test_suite():
    return unittest.TestSuite([TestGps])

if __name__ == '__main__':
    unittest.main()
