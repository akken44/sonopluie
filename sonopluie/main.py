# -*- coding: utf-8 -*-
# Import used package
import sys
import threading
import time
import os
from RPi import GPIO
from neopixel import Color, Adafruit_NeoPixel
import subprocess

# Import our package
from .gps import GPS
from .ble import BLE
from .scenario import Scenario

# By default, a scan last 2 seconds
TIME_SCAN_BLE = 2

# Define GPIO pins
PIN_BTN = 24
PIN_LED = 12
# This pin is used to send a high level to the led to be able to turn it on (it is connected to the 5V pin of the Led)
PIN_PWR_LED = 16

# Define number of seconds to trigger reset and shutdown by pushing the button
SHORT_PRESS = 0.2
LONG_PRESS = 3

# Define color of the led (Green, Red ,Blue)
COLOR_BOOT = Color(255, 255, 255)  # White
COLOR_BEACON = Color(0, 0, 255)  # Blue
COLOR_GPS = Color(255, 0, 0)  # Green
COLOR_NOGPS = Color(0, 255, 0)  # Red
COLOR_RESET = Color(0, 255, 255)  # Violet
COLOR_SHUTDOWN = Color(50, 255, 0)  # Orange


class App(object):

    def __init__(self, debug=False, xmlfile='/boot/sonopluie/scenario.xml',
                 snddir='/boot/sonopluie/sound/'):
        if not debug:
            sys.stdout = None

        # True : GPS
        # False : Beacon
        self.mode = True

        self.initBtnLed()
        self.initGPS()
        self.initBLE()
        self.initScenario(xmlfile, snddir)

    def initBtnLed(self):
        # Init GPIOs
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_BTN, GPIO.IN)  # Tell the button is an input

        GPIO.setup(PIN_PWR_LED, GPIO.OUT)  # Tell the led is an output
        # Send an high level to the 5V pin of the led
        GPIO.output(PIN_PWR_LED, True)

        # Start up the led
        # Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
        #                   LED_INVERT, LED_BRIGHTNESS)
        self.led = Adafruit_NeoPixel(1, PIN_LED, 800000, 5, False, 100)
        self.led.begin()
        # This var is set False once the user shutdown the system
        self.led.active = True
        self.updateLed(COLOR_BOOT)

    def initGPS(self):
        self.gps = GPS()
        self.gps.updatePosition()
        self.latitude = self.gps.getLatitude()
        self.longitude = self.gps.getLongitude()

    def initBLE(self):
        self.actualBeacon = None
        self.validNewBeacon = 0
        self.validNoBeacon = 0
        self.ble = BLE()

    def initScenario(self, xmlfile, snddir):
        self.scenario = Scenario(xmlfile, snddir)

    def main(self):
        # Starting threads
        threading.Thread(target=self.checkBtn).start()
        threading.Thread(target=self.updateGPS).start()
        threading.Thread(target=self.updateBLE).start()
        threading.Thread(target=self.scenario.checkEndEvent).start()

    def checkBtn(self):

        while True:

            durationPress = 0

            while GPIO.input(PIN_BTN) > 0 and durationPress <= LONG_PRESS:
                durationPress += 0.1
                time.sleep(0.1)

            # If it's a long press
            if durationPress >= LONG_PRESS:
                self.updateLed(COLOR_SHUTDOWN)
                self.led.active = False

                # Use subprocess instead of sys.os() to avoid the waiting of the return of the cmd
                subprocess.Popen(['shutdown', 'now'])
                # Use this instead of sys.exit() cause it will kill the thread only
                os._exit(1)

            # If it's a short press
            elif durationPress >= SHORT_PRESS:
                self.updateLed(COLOR_RESET)
                self.scenario.resetScenario()
                self.actualBeacon = None

            time.sleep(0.1)

    def updateLed(self, color):
        if self.led.active:
            # Setting the new color of the led
            self.led.setPixelColor(0, color)
            # Update the led
            self.led.show()

    def updateGPS(self):
        while True:

            time.sleep(0.5)

            # if no beacon is detected
            if self.mode:
                self.updateLed(COLOR_GPS)

                self.gps.updatePosition()

                _latitude = self.gps.getLatitude()
                _longitude = self.gps.getLongitude()

                # If GPS position has been found
                if _latitude is None or _longitude is None:
                    self.updateLed(COLOR_NOGPS)
                    continue

                # Avoid some bugs when for example longitude is -1.2983687
                #  and the next time is 1.2983687
                if int(self.latitude) != int(_latitude) or int(self.longitude) != int(_longitude):
                    continue

                self.latitude = _latitude
                self.longitude = _longitude

                print ('Latitude : ', self.latitude)
                print ('Longitude : ', self.longitude)

                self.scenario.calculGps(self.latitude, self.longitude)

    def updateBLE(self):

        while True:
            # scan(timeout in seconds, UUID) - Here b9407f30f5f8466eaff925556b57fe6d is the default Estimote UUID
            beaconsScanned = self.ble.scan(TIME_SCAN_BLE, 'b9407f30f5f8466eaff925556b57fe6d')

            if beaconsScanned:
                self.updateLed(COLOR_BEACON)

                self.mode = False
                self.validNoBeacon = 0

                closestBeacon = None

                # Get the closest beacon scanned (RSSI is the power receive indice)
                for beacon in beaconsScanned:
                    if not closestBeacon:
                        closestBeacon = beacon

                    if beacon['RSSI'] > closestBeacon['RSSI']:
                        closestBeacon = beacon

                # Check if there is a new beacon is detected closer, and start a new scan to be sure if so
                if self.actualBeacon is not None and not closestBeacon['MACADDR'] == self.actualBeacon['MACADDR'] and self.validNewBeacon < 1:
                    self.validNewBeacon += 1
                    print ('New beacon :', closestBeacon['MACADDR'], '(', self.validNewBeacon, 'try)')
                    continue

                self.actualBeacon = closestBeacon
                self.validNewBeacon = 0

                print ('-------------')
                print (self.actualBeacon['MACADDR'], ':')
                print ('Major :', self.actualBeacon['MAJOR'])
                print ('Minor :', self.actualBeacon['MINOR'])
                print ('RSSI :', self.actualBeacon['RSSI'])

                # uid is the concat of major + minor in the scenario.xml
                uid = int(str(self.actualBeacon['MAJOR']) + str(self.actualBeacon['MINOR']))
                self.scenario.calculBeacon(uid)

            else:
                # If no beacon is detected, we check 5 times to be sure
                if self.actualBeacon is not None and self.validNoBeacon < 5:
                    self.validNoBeacon += 1
                    print ('No beacon detected,', self.validNoBeacon, 'try')
                    continue

                self.validNoBeacon = 0
                self.actualBeacon = None
                self.mode = True

            time.sleep(0.5)

if __name__ == '__main__':
    app = App()
    app.main()
