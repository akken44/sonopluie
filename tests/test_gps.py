# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock, patch


# ----------------------------------------------------------------------------
# my mock classes
# ----------------------------------------------------------------------------
class MockSerial(object):
    def __init__(self):
        self.data = '$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47'.encode('utf8')

    def readline(self):
        return (self.data)


def open_serial_port(port, baudrate):
    return MockSerial()


patch.dict(
    "sys.modules",
    serial=MagicMock(Serial=open_serial_port)
).start()

from sonopluie import gps


class TestGps(unittest.TestCase):
    def setUp(self):
        self.mygps = gps.GPS()

    def test_can_init_gps_object(self):
        self.assertIsInstance(self.mygps, gps.GPS)

    def test_can_update_and_read_posision(self):
        self.mygps.updatePosition()
        self.assertEqual(self.mygps.getLongitude(), 11.516666666666667)
        self.assertEqual(self.mygps.getLatitude(), 48.11729999999999)
        self.mygps.ser.data = '$GPGGA,123519,4810.038,N,01152.000,E,1,08,0.9,545.4,M,46.9,M,,*47'.encode('utf8')
        self.mygps.updatePosition()
        self.assertEqual(self.mygps.getLongitude(), 11.866666666666667)
        self.assertEqual(self.mygps.getLatitude(), 48.16729999999999)


# def test_suite():
#     return unittest.TestSuite([TestGps])

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
