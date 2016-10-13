# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock, patch


# ----------------------------------------------------------------------------
# my mock classes
# ----------------------------------------------------------------------------
class MockSerial(object):

    def readline(self):
        return ("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,"
                "545.4,M,46.9,M,,*47".encode('utf8'))


def open_serial_port(port, baudrate):
    return MockSerial()


patch.dict(
    "sys.modules",
    serial=MagicMock(Serial=open_serial_port)
).start()

from sonopluie import gps


class TestGps(unittest.TestCase):

    def test_can_init_gps_object(self):
        mygps = gps.GPS()
        self.assertIsInstance(mygps, gps.GPS)


# def test_suite():
#     return unittest.TestSuite([TestGps])

if __name__ == '__main__':
    unittest.main()
