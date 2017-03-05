from datetime import datetime
import serial, pynmea2, json
import time, sys, signal, atexit
from upm import pyupm_bmp280 as sensorObj

class nv08c_nrt():
    def __init__(self, port, brate):
        self.port   = port
        self.brate  = brate

    def read(self):
        ser = None
        reader = pynmea2.NMEAStreamReader()
        if ser is None:
            try:
                ser = serial.Serial(self.port, baudrate=self.brate, timeout=5.0)
            except serial.SerialException:
                print('could not connect to %s' % port)
                time.sleep(5.0)
        dat = ser.read(256) #reads up to n bytes of data streamed to the port
        for msg in reader.next(dat):
            #print type(msg)
            if isinstance(msg, pynmea2.types.talker.GGA): #extract data from sentence nmea GPGGA
                #print msg
                d = str(datetime.now().date())
                t = d+" "+str(msg.timestamp)
                lat = msg.latitude
                lon = msg.longitude
                alt = msg.altitude
                return {"lat":str(lat),"lon":str(lon),"alt":alt, "t":t}
        return {}



class bme280_nrt():
    def __init__(self):
        self.s = sensorObj.BME280()
    
    def read(self):
        self.s.update()
        TD  = self.s.getTemperature()
        PR  = self.s.getPressure()
        HR  = self.s.getHumidity()
        Alt = self.s.getAltitude()
        return {"TD":str(TD),"PR":str(PR),"HR":str(HR), "AltComp":str(Alt)} 
