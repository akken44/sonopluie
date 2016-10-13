# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock, patch

mockRpi = MagicMock()
mockNeopixel = MagicMock()
mockSerial = MagicMock()
mockBluetooth = MagicMock()
patch.dict("sys.modules", RPi=mockRpi, neopixel=mockNeopixel,
           serial=mockSerial, bluetooth=mockBluetooth).start()

from sonopluie import App


class TestScenario(unittest.TestCase):

    def test_gps(self):
        app = App()
        print("TEST GPS")


def test_suite():
    return unittest.TestSuite([TestScenario])

if __name__ == '__main__':
    unittest.main()
