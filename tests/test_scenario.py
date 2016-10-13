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


# ----------------------------------------------------------------------------
# MagicMock stuff
# ----------------------------------------------------------------------------
mockRpi = MagicMock()
mockNeopixel = MagicMock()
mockSerial = MagicMock(Serial=open_serial_port)
mockBluetooth = MagicMock()
patch.dict("sys.modules", RPi=mockRpi, neopixel=mockNeopixel,
           serial=mockSerial, bluetooth=mockBluetooth).start()
XMLFILE = 'tests/scenario0.xml'


# ----------------------------------------------------------------------------
# import mocked classes
# ----------------------------------------------------------------------------
from sonopluie import App


# ----------------------------------------------------------------------------
# tests
# ----------------------------------------------------------------------------
class TestScenario(unittest.TestCase):

    def test_gps(self):
        app = App(debug=True, xmlfile=XMLFILE)


# ----------------------------------------------------------------------------
# testsuite
# ----------------------------------------------------------------------------
def test_suite():
    return unittest.TestSuite([TestScenario])

if __name__ == '__main__':
    unittest.main()
