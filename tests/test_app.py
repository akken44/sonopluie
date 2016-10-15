# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock, patch

from .helper_serial import MockSerial
from .test_ble import MockBluez

# ----------------------------------------------------------------------------
# my mock classes
# ----------------------------------------------------------------------------
class MockRpiGPIO(object):

    BCM = 0
    IN = 1
    OUT = 2
    pins_inout = {}
    pins_status = {}

    @classmethod
    def setup(cls, pin_number, inout):
        cls.pins_inout[pin_number] = inout

    @classmethod
    def setmode(cls, m):
        pass

    @classmethod
    def output(cls, pin_number, status):
        cls.pins_status[pin_number] = status


class Neopixel(object):

    def __init__(self, a, b, c, d, e, f):
        pass

    def begin(self):
        pass

    def setPixelColor(self, n, color):
        self.color = color

    def show(self):
        pass


class Color(object):

    def __init__(self, g, r, b):
        self.green = g
        self.red = r
        self.blue = b


# ----------------------------------------------------------------------------
# MagicMock stuff
# ----------------------------------------------------------------------------
mockRpi = MagicMock(GPIO=MockRpiGPIO)
mockNeopixel = MagicMock(Adafruit_NeoPixel=Neopixel, Color=Color)
mockSerial = MagicMock(Serial=MockSerial)
mockPygame = MagicMock()
patch.dict('sys.modules', RPi=mockRpi, neopixel=mockNeopixel,
           serial=mockSerial, bluetooth=MockBluez(),
           pygame=mockPygame).start()


# ----------------------------------------------------------------------------
# import mocked classes
# ----------------------------------------------------------------------------
from sonopluie.main import App
from sonopluie import main


# ----------------------------------------------------------------------------
# tests
# ----------------------------------------------------------------------------
XMLFILE = 'tests/scenario0.xml'
SNDDIR = 'tests/snd'


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = App(debug=True, xmlfile=XMLFILE, snddir=SNDDIR)

    def test_init_gps(self):
        lat = self.app.gps.convertCoord(MockSerial().lat)
        lon = self.app.gps.convertCoord(MockSerial().lon)
        self.assertEqual(self.app.latitude, lat)
        self.assertEqual(self.app.longitude, lon)

    def test_init_btn_led(self):
        inout = MockRpiGPIO.pins_inout[main.PIN_BTN]
        self.assertEqual(inout, MockRpiGPIO.IN)

        inout = MockRpiGPIO.pins_inout[main.PIN_PWR_LED]
        self.assertEqual(inout, MockRpiGPIO.OUT)

        status = MockRpiGPIO.pins_status[main.PIN_PWR_LED]
        self.assertEqual(status, True)

        color = self.app.led.color
        self.assertEqual(color.red, main.COLOR_BOOT.red)
        self.assertEqual(color.green, main.COLOR_BOOT.green)
        self.assertEqual(color.blue, main.COLOR_BOOT.blue)

    def test_init_scenario(self):
        self.assertEqual(len(self.app.scenario.listAudio_origin), 2)

        a0 = self.app.scenario.listAudio_origin[0]
        self.assertEqual(a0.id, 'Beacon1')
        self.assertEqual(a0.path, 'escargot.ogg')
        self.assertEqual(a0.volume, 100)
        self.assertEqual(a0.uid, 115557701)
        self.assertEqual(a0.active, True)
        self.assertEqual(a0.loop, True)
        self.assertEqual(a0.name, 'Beacon1')
        end_event = a0.endEvent[0]
        self.assertEqual(end_event['target'], 'P1')
        self.assertEqual(end_event['action'], 'active')
        self.assertEqual(end_event['active'], 'on')

        a1 = self.app.scenario.listAudio_origin[1]
        self.assertEqual(a1.id, 'P1')
        self.assertEqual(a1.path, 'pont.ogg')
        self.assertEqual(a1.volume, 100)
        self.assertEqual(a1.active, False)
        self.assertEqual(a1.loop, False)
        self.assertEqual(a1.name, 'P1')
        lat, lon = a1.location
        self.assertEqual(lat, '48.120154')
        self.assertEqual(lon, '-1.627737')
        start_event = a1.startEvent[0]
        self.assertEqual(start_event['target'], 'Beacon1')
        self.assertEqual(start_event['action'], 'active')
        self.assertEqual(start_event['active'], 'off')
        end_event = a1.endEvent[0]
        self.assertEqual(end_event['target'], 'Beacon1')
        self.assertEqual(end_event['action'], 'active')
        self.assertEqual(end_event['active'], 'on')


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
