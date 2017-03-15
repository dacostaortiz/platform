import time, sys, signal, atexit
from upm import pyupm_bmp280 as sensorObj

class nrt():
    def __init__(self):
        self.s = sensorObj.BME280()
    
    def read(self):
        self.s.update()
        TD  = self.s.getTemperature()
        PR  = self.s.getPressure()
        HR  = self.s.getHumidity()
        Alt = self.s.getAltitude()
        return {"TD":str(TD),"PR":str(PR),"HR":str(HR), "AltComp":str(Alt)} 
