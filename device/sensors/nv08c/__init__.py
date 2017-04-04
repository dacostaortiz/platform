from datetime import datetime
import serial, pynmea2, json, os, subprocess, psutil

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
        dat = ser.read(128) #reads up to n bytes of data streamed to the port
        for msg in reader.next(dat):
            if isinstance(msg, pynmea2.types.talker.GGA): #extract data from sentence nmea GPGGA
                d = str(datetime.now().date())
                t = d+" "+str(msg.timestamp)
                lat = msg.latitude
                lon = msg.longitude
                alt = msg.altitude
                return {"lat":str(lat),"lon":str(lon),"alt":alt, "t":t}
        return {}

class batch():
    def __init__(self, port, brate, data_dir, fname):
        self.port       = port
        self.brate      = brate
        self.fname      = fname
        self.data_dir   = data_dir
        print port, brate, fname, data_dir

    def start(self):
        inp         = "serial://"+self.port+":"+self.brate+":8:o:1:off#nvs"
        out         = "file://"+self.data_dir+"incoming/"+self.fname+"%y%n%H.nvs"
        config_file = "/gnss/datatools/conf/nvs08_10hz.cmd"
        try:
            std_out = open('/var/log/str2str.out','r')
            std_out.close()
            std_err = open('/var/log/str2str.err','r')
            std_err.close()
        except:
            std_out = open('/var/log/str2str.out','w')
            std_out.close()
            std_err = open('/var/log/str2str.err','w')
            std_err.close()
        p = subprocess.Popen('/gnss/datatools/bin/str2str -in '+inp+':S=1 -out '+out+' -c '+config_file+' -f 0 > '+std_err.name+' 2> '+std_out.name, shell=True)
        pid = p.pid
        pidfile = open('/var/run/nv08c.bat.pid','w')
        pidfile.write(str(pid))
        pidfile.close()
        print p, p.pid 
        #return pid

    def is_alive(self):
        try:
            pid_file = open('/var/run/nv08c.bat.pid', 'r')
            pid = pid_file.read()
            pid_file.close()

            if psutil.pid_exists(int(pid)):
                print "process nv08c.bat is running", pid
                return {'nv08c.bat':'alive'}
            else:
                print "process nv08c.bat is dead"
                return {'nv08c.bat':'dead'}
        except:
            print "pid file doesn't exist, process is dead"
            return {'nv08c.bat':'dead'}
        


