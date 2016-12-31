from dev_gnss import *
import time
import uuid
import ConfigParser
import pycurl
import json

#device id must to be unique, we could use mac as id
mac_num = hex(uuid.getnode()).replace('0x','')
mac     = ':'.join(mac_num[i : i + 2] for i in range(0,11,2))

#load configurations
config  = ConfigParser.ConfigParser()
config.readfp(open(r'device.cfg'))
profile = config.get('Device Config', 'profile')
gnss_port    = config.get('Device Config', 'gnss_dev')


gnss = gnss_nmea()         

while 1:
    t,lat,lon,alt = gnss.read_serial(gnss_port)
    content = {"lat":lat,"lon":lon,"alt":alt}
    data = {"dev_id":mac,"prof_id":profile,"dev_time":t,"content":content}
    data = json.dumps(data)
    #print data
    c = pycurl.Curl()
    c.setopt(pycurl.URL, '192.168.0.110:9050/data/') #configure remote ip address and port
    c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, data)
    #c.setopt(pycurl.VERBOSE, 1)
    c.perform()
    c.close()
