# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock, patch


class SerialException(Exception):
    '''
    Base class for serial port related exceptions.
    '''
    pass


class MockSerial(object):
    have_gps_data = True
    lat = 4807.038
    lat_dir = 'N'
    lon = 01131.000
    lon_dir = 'E'

    def __init__(self, *args, **kwargs):
        pass

    def readline(self):
        if self.have_gps_data:
            return ('$GPGGA,123519,{lat},{lat_dir},{lon},{lon_dir},1,08,0.9,'
                    '545.4,M,46.9,M,,*47'.format(lat=self.lat,
                                                 lat_dir=self.lat_dir,
                                                 lon=self.lon,
                                                 lon_dir=self.lon_dir,
                                                 )
                    .encode('utf8'))
        else:
            error = SerialException()
            raise error

patch.dict(
    "sys.modules",
    serial=MagicMock(Serial=MockSerial),
).start()

from sonopluie import gps  # nopep8 Import after for mock


class TestGps(unittest.TestCase):
    def setUp(self):
        self.mygps = gps.GPS()
        MockSerial.have_gps_data = True
        MockSerial.lat = 4807.038
        MockSerial.lon = 01131.000
        MockSerial.lat_dir = 'N'
        MockSerial.lon_dir = 'E'

    def test_can_init_gps_object(self):
        self.assertIsInstance(self.mygps, gps.GPS)

    def test_can_update_and_read_posision(self):
        self.mygps.updatePosition()
        self.assertEqual(self.mygps.getLongitude(), 11.516666666666667)
        self.assertEqual(self.mygps.getLatitude(), 48.11729999999999)

        MockSerial.lat = 4810.038
        MockSerial.lon = 01152.000
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
        MockSerial.lat = ''
        MockSerial.lat_dir = ''
        MockSerial.lon = ''
        MockSerial.lon_dir = ''
        self.assertEqual(self.mygps.updatePosition(), False)

    def test_gps_return_empty_data(self):
        MockSerial.lat = None
        MockSerial.lat_dir = None
        MockSerial.lon = None
        MockSerial.lon_dir = None
        self.assertEqual(self.mygps.updatePosition(), False)

    def test_gps_return_negative_data(self):
        MockSerial.lat_dir = 'S'
        MockSerial.lon_dir = 'W'
        self.mygps.updatePosition()
        self.assertEqual(self.mygps.getLongitude(), -11.516666666666667)
        self.assertEqual(self.mygps.getLatitude(), -48.11729999999999)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
