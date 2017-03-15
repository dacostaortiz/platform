from datetime import datetime
import serial, pynmea2, json

class nrt():
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
                d = str(datetime.now().date())
                t = d+" "+str(msg.timestamp)
                lat = msg.latitude
                lon = msg.longitude
                alt = msg.altitude
                return {"lat":str(lat),"lon":str(lon),"alt":alt, "t":t}
        return {}
