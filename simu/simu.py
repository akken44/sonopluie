# -*- coding: utf-8 -*-
import argparse
import math
from unittest.mock import MagicMock, patch

# ----------------------------------------------------------------------------
# import mocked classes
# ----------------------------------------------------------------------------
from sonopluie.main import App


# ----------------------------------------------------------------------------
# my mock classes
# ----------------------------------------------------------------------------
class MockSerial(object):

    def __init__(self):
        self.__gps_file = None
        self.lats = []
        self.lons = []
        self.idx = None

    def readline(self):
        if self.idx is not None:
            lat = self.convertCoord(self.lats[self.idx])
            lon = self.convertCoord(self.lons[self.idx])
            self.idx += 1

            if self.idx > len(self.lats)-1:
                self.idx = 0

            return ('$GPGGA,123519,{0},N,{1},E,1,08,0.9,'
                    '545.4,M,46.9,M,,*47'.format(lat, lon)
                    .encode('utf8'))
        else:
            return ('$GPGGA,123519,{0},N,{1},E,1,08,0.9,'
                    '545.4,M,46.9,M,,*47'.format(0, 0)
                    .encode('utf8'))

    def convertCoord(self, coord):
        firsttwodigits = math.floor(coord / 100)
        nexttwodigits = coord - (firsttwodigits * 100)
        realCoord = firsttwodigits + nexttwodigits / 60
        return realCoord

    @property
    def gps_file(self):
        return self.__gps_file

    @gps_file.setter
    def gps_file(self, f):
        self.__gps_file = f
        self.idx = 0

        with open(self.__gps_file, 'r') as f:
            for l in f:
                lat, lon = l.replace('\n', '').split(' ')
                self.lats.append(float(lat))
                self.lons.append(float(lon))


def open_serial_port(port, baudrate):
    return MockSerial()


class MockBluetooth(object):

    def __init__(self):
        pass

    def getsockopt(self, a, b, c):
        pass

    def setsockopt(self, a, b, c):
        pass

    def settimeout(self, t):
        pass

    def recv(self, a):
        return bytearray("ABCDEF".encode('utf8'))


def open_bluetooth(dev_id):
    return MockBluetooth()


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

    @classmethod
    def input(cls, pin):
        return cls.pins_inout[pin]


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
mockSerial = MagicMock(Serial=open_serial_port)
mockBluetooth = MagicMock()
mockBluetooth._bluetooth.hci_open_dev = open_bluetooth
mockPygame = MagicMock()
patch.dict('sys.modules', RPi=mockRpi, neopixel=mockNeopixel,
           serial=mockSerial, bluetooth=mockBluetooth,
           pygame=mockPygame).start()


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    # arg parse
    descr = 'Sonopluie simulator!!!!!'
    parser = argparse.ArgumentParser(description=descr)

    gps_help = 'GPS file'
    parser.add_argument('gps', metavar='gps', type=str, help=gps_help)

    snddir = 'Scenario XML file'
    parser.add_argument('scn', metavar='scn', type=str, help=gps_help)

    snddir = 'Sound directory'
    parser.add_argument('snd', metavar='snd', type=str, help=gps_help)

    args = parser.parse_args()

    # read data
    app = App(debug=True, xmlfile=args.scn, snddir=args.snd)
    app.gps.ser.gps_file = args.gps
    app.main()
