# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock, patch


class MockBluez(object):
    SOL_HCI = None
    HCI_FILTER = None
    normal_open_dev = True

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def hci_open_dev(self, *args, **kwargs):
        if self.normal_open_dev:
            return MockBluez()
        else:
            raise IOError

    def getsockopt(self, *args, **kwargs):
        pass

    def hci_send_cmd(self, *args, **kwargs):
        pass

patch.dict(
    "sys.modules",
    bluetooth=MagicMock(_bluetooth=MockBluez),
).start()

from sonopluie import ble


class TestBle(unittest.TestCase):
    def test_can_init_and_fail(self):
        MockBluez.normal_open_dev = False
        with self.assertRaises(SystemExit):
            ble.BLE()

    def test_can_init(self):
        ble.BLE()
