from datetime import datetime
import serial
import pynmea2
import json

class nv08c_nmea():
    def read(self, port, brate=115200):
        ser = None
        reader = pynmea2.NMEAStreamReader()
        if ser is None:
            try:
                ser = serial.Serial(port, baudrate=brate, timeout=5.0)
            except serial.SerialException:
                print('could not connect to %s' % port)
                time.sleep(5.0)

        dat = ser.read(128) #reads up to 96 bytes of data (timeout)
        for msg in reader.next(dat):
            if isinstance(msg, pynmea2.types.talker.GGA): #extract data from sentence nmea GPGGA
                #print msg
                #t   = msg.datetime
                d = str(datetime.now().date())
                t = d+" "+str(msg.timestamp)
                lat = msg.latitude
                lon = msg.longitude
                alt = msg.altitude
                
        return t, {"lat":str(lat),"lon":str(lon),"alt":alt}

