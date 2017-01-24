from __future__ import print_function
import time, sys, signal, atexit
from upm import pyupm_bmp280 as sensorObj

class bme280_all():
    sensor = sensorObj.BME280()
    def read(self):
        self.sensor.update()
        TD = self.sensor.getTemperature()
        PR = self.sensor.getPressure()
        HR = self.sensor.getHumidity()
        Alt = self.sensor.getAltitude()
        return {"TD":str(TD),"PR":str(PR),"HR":str(HR), "AltComp":str(Alt)} 
