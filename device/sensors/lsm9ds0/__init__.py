#!/usr/bin/python
# Based on the example given in https://github.com/intel-iot-devkit/upm/blob/master/examples/python/lsm9ds0.py
###############################################################################
# Author: Jon Trulson <jtrulson@ics.com>
# Copyright (c) 2015 Intel Corporation.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
###############################################################################

from __future__ import print_function
import time, sys, signal, atexit
from upm import pyupm_lsm9ds0 as sensorObj

class nrt():
    def __init__(self):
        # Instantiate an LSM9DS0 using default parameters (bus 1, gyro addr 6b, xm addr 1d)
        self.s = sensorObj.LSM9DS0()
        self.s.init()
        
        self.x = sensorObj.new_floatp()
        self.y = sensorObj.new_floatp()
        self.z = sensorObj.new_floatp()
        
    ## Exit handlers ##
    # This function stops python from printing a stacktrace when you hit control-c
    def SIGINTHandler(signum, frame):
        raise SystemExit

    # This function lets you run code on exit
    def exitHandler():
        print("Exiting")
        sys.exit(0)
    # Register exit handlers
    #atexit.register(exitHandler)
    #signal.signal(signal.SIGINT, SIGINTHandler)

    def read(self):
        content = {}
        self.s.update()
        self.s.getAccelerometer(self.x, self.y, self.z)
        content.update({"AX": sensorObj.floatp_value(self.x),
                        "AY": sensorObj.floatp_value(self.y),
                        "AZ": sensorObj.floatp_value(self.z)})

        self.s.getGyroscope(self.x, self.y, self.z)
        content.update({"GX": sensorObj.floatp_value(self.x),
                        "GY": sensorObj.floatp_value(self.y),
                        "GZ": sensorObj.floatp_value(self.z)})

        self.s.getMagnetometer(self.x, self.y, self.z)
        content.update({"MX": sensorObj.floatp_value(self.x),
                        "MY": sensorObj.floatp_value(self.y),
                        "MZ": sensorObj.floatp_value(self.z)})

        content.update({"Temp IMU": self.s.getTemperature()})
        #print(content)
        return content
