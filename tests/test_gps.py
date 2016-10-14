# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock, patch

from .helper_serial import MockSerial, SerialException

patch.dict(
    "sys.modules",
    serial=MagicMock(Serial=MockSerial),
).start()

from sonopluie import gps


class TestGps(unittest.TestCase):
    def setUp(self):
        self.mygps = gps.GPS()
        MockSerial.have_gps_data = True
        MockSerial.data = '$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47'.encode('utf8')

    def test_can_init_gps_object(self):
        self.assertIsInstance(self.mygps, gps.GPS)

    def test_can_update_and_read_posision(self):
        self.mygps.updatePosition()
        self.assertEqual(self.mygps.getLongitude(), 11.516666666666667)
        self.assertEqual(self.mygps.getLatitude(), 48.11729999999999)

        MockSerial.data = '$GPGGA,123519,4810.038,N,01152.000,E,1,08,0.9,545.4,M,46.9,M,,*47'.encode('utf8')
        self.mygps.updatePosition()
        self.assertEqual(self.mygps.getLongitude(), 11.866666666666667)
        self.assertEqual(self.mygps.getLatitude(), 48.16729999999999)

    @patch('serial.SerialException', new_callable=lambda: SerialException)
    def test_can_manage_serial_exception(self, mock_serial):
        self.mygps.updatePosition()
        with self.assertRaises(SerialException):
            MockSerial.have_gps_data = False
            self.mygps.updatePosition()

    def test_gps_does_get_real_data(self):
        MockSerial.data = '$GPGGA,bad_data,M,46.9,M,,*47'.encode('utf8')
        self.assertEqual(self.mygps.updatePosition(), False)

    def test_gps_return_empty_data(self):
        MockSerial.data = '$GPGGA,,,,,,,,,,,,,,'.encode('utf8')
        self.assertEqual(self.mygps.updatePosition(), False)

    def test_gps_return_negative_data(self):
        MockSerial.data = '$GPGGA,123519,4807.038,S,01131.000,W,1,08,0.9,545.4,M,46.9,M,,*47'.encode('utf8')
        self.mygps.updatePosition()
        self.assertEqual(self.mygps.getLongitude(), -11.516666666666667)
        self.assertEqual(self.mygps.getLatitude(), -48.11729999999999)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
