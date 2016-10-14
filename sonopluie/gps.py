# -*- coding: utf-8 -*-
import serial
from math import sin, cos, sqrt, atan2, radians, floor
import re


class GPS(object):

    def __init__(self):
        # Init the serial communication with the GPS
        self.ser = serial.Serial(port='/dev/ttyAMA0', baudrate=9600)
        self.latitude = None
        self.longitude = None

    ''' Used to convert GPS latitude longitude to cardinal value '''
    def convertCoord(self, coord):
        firsttwodigits = floor(coord / 100)
        nexttwodigits = coord - (firsttwodigits * 100)
        realCoord = firsttwodigits + nexttwodigits / 60

        return realCoord

    ''' Update the latitude and lagitude attribute '''
    def updatePosition(self):

        line = ''

        while not '$GPGGA' in line:
            line = self.ser.readline().decode('latin-1')

        # Regex used to parse the trame
        m = re.search(r'GPGGA,(\d*\.?\d*),(\d*\.?\d*),([A-Z]?),(\d*\.?\d*),([A-Z]?),', line)

        if not m:     # If unable to read the trame
            print ('Unable to connect to the GPS')
            return False

        _latitude = m.groups()[1]
        _latDirection = m.groups()[2]
        _longitude = m.groups()[3]
        _longDirection = m.groups()[4]

        # If latitude and lagitude parsed are empty, it's that the GPS didn't find his position yet
        if not _latitude or not _longitude:
            print ('Waiting for positionning...')
            self.latitude = None
            self.longitude = None
            return False

        _latitude = self.convertCoord(float(_latitude))
        _longitude = self.convertCoord(float(_longitude))

        # If latitude is S, it is reversed
        if _latDirection is 'S':
            _latitude = -_latitude
        # If longitude is W, it is reversed
        if _longDirection is 'W':
            _longitude = -_longitude

        self.latitude = _latitude
        self.longitude = _longitude

        return True

    def getLatitude(self):
        return self.latitude

    def getLongitude(self):
        return self.longitude
