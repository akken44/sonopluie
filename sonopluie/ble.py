# -*- coding: utf-8 -*-
# BLE iBeaconScanner based on https://github.com/adamf/BLE/blob/master/ble-scanner.py
# JCS 06/07/14

DEBUG = True
# BLE scanner based on https://github.com/adamf/BLE/blob/master/ble-scanner.py
# BLE scanner, based on https://code.google.com/p/pybluez/source/browse/trunk/examples/advanced/inquiry-with-rssi.py

# https://github.com/pauloborges/bluez/blob/master/tools/hcitool.c for lescan
# https://kernel.googlesource.com/pub/scm/bluetooth/bluez/+/5.6/lib/hci.h for opcodes
# https://github.com/pauloborges/bluez/blob/master/lib/hci.c#L2782 for functions used by lescan

# performs a simple device inquiry, and returns a list of ble advertizements
# discovered device

# NOTE: Python's struct.pack() will add padding bytes unless you make the endianness explicit. Little endian
# should be used for BLE. Always start a struct.pack() format string with '<'

import sys
import struct
import time
from bluetooth import _bluetooth as bluez

LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS = 0x00
LE_RANDOM_ADDRESS = 0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE = 7
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C
OCF_LE_CREATE_CONN = 0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_ADVERTISING_REPORT = 0x02
EVT_LE_CONN_UPDATE_COMPLETE = 0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE = 0x04

# Advertisment event types
ADV_IND = 0x00
ADV_DIRECT_IND = 0x01
ADV_SCAN_IND = 0x02
ADV_NONCONN_IND = 0x03
ADV_SCAN_RSP = 0x04


class BLE(object):

    def __init__(self):

        dev_id = 0

        try:
            self.sock = bluez.hci_open_dev(dev_id)
        except:
            print ('Error accessing bluetooth device...')
            sys.exit(1)

        self.hci_le_set_scan_parameters()
        self.hci_enable_le_scan()

    def returnnumberpacket(self, pkt):
        myInteger = 0
        multiple = 256
        for c in pkt:
            myInteger +=  c * multiple
            multiple = 1
        return myInteger

    def returnstringpacket(self, pkt):
        myString = '';
        for c in pkt:
            myString +=  '%02x' % c
        return myString

    def hci_enable_le_scan(self):
        self.hci_toggle_le_scan(0x01)

    def hci_disable_le_scan(self):
        self.hci_toggle_le_scan(0x00)

    def hci_toggle_le_scan(self, enable):
    # hci_le_set_scan_enable(dd, 0x01, filter_dup, 1000);
    # memset(&scan_cp, 0, sizeof(scan_cp));
    # uint8_t         enable;
    #        uint8_t         filter_dup;
    #        scan_cp.enable = enable;
    #        scan_cp.filter_dup = filter_dup;
    #
    #        memset(&rq, 0, sizeof(rq));
    #        rq.ogf = OGF_LE_CTL;
    #        rq.ocf = OCF_LE_SET_SCAN_ENABLE;
    #        rq.cparam = &scan_cp;
    #        rq.clen = LE_SET_SCAN_ENABLE_CP_SIZE;
    #        rq.rparam = &status;
    #        rq.rlen = 1;

    #        if (hci_send_req(dd, &rq, to) < 0)
    #                return -1;
        cmd_pkt = struct.pack('<BB', enable, 0x00)
        bluez.hci_send_cmd(self.sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

    def hci_le_set_scan_parameters(self):
        old_filter = self.sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

        SCAN_RANDOM = 0x01
        OWN_TYPE = SCAN_RANDOM
        SCAN_TYPE = 0x01

    def scan(self, timeout=10, UUID=None):

        old_filter = self.sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

        # perform a device inquiry on bluetooth device #0
        # The inquiry should last 8 * 1.28 = 10.24 seconds
        # before the inquiry is performed, bluez should flush its cache of
        # previously discovered devices
        flt = bluez.hci_filter_new()
        bluez.hci_filter_all_events(flt)
        bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
        self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
        self.sock.settimeout(timeout)

        beacons = []

        timeStart = time.time()

        while (time.time() - timeStart) < timeout:

            try:
                pkt = self.sock.recv(255)
            except bluez.timeout:
                return None

            ptype, event, plen = struct.unpack('BBB', pkt[:3])

            if event == LE_META_EVENT:

                subevent = pkt[3]
                pkt = pkt[4:]

                if subevent == EVT_LE_CONN_COMPLETE:
                    le_handle_connection_complete(pkt)

                newBLE = {}

                # Parse the trame
                newBLE['MACADDR'] = ':'.join(('%012X' % int.from_bytes(pkt[3: 9], byteorder='big', signed=False))[i:i+2] for i in range(0, 12, 2))
                newBLE['UUID'] = self.returnstringpacket(pkt[-22: -6])
                newBLE['MAJOR'] = self.returnnumberpacket(pkt[-6: -4])
                newBLE['MINOR'] = self.returnnumberpacket(pkt[-4: -2])
                newBLE['TXPOWER'] = pkt[-2]
                newBLE['RSSI'] = pkt[-1]

                addThisBLE = True

                # If this beacon just scanned has not already been scanned
                for beacon in beacons:
                    if beacon['MACADDR'] == newBLE['MACADDR']:
                        addThisBLE = False

                # If this beacon is an Estimote (default UUID)
                if UUID is not None and not newBLE['UUID'] == UUID:
                    addThisBLE = False

                # If so, we add this beacon
                if addThisBLE:
                    beacons.append(newBLE)

        self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)

        return beacons
