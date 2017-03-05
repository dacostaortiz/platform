import dev_gnss, dev_sensor
import time
import uuid
import ConfigParser
import pycurl
import json

#device id must to be unique, we could use mac as id
mac_num = hex(uuid.getnode()).replace('0x','')
mac     = ':'.join(mac_num[i : i + 2] for i in range(0,11,2))

#load configurations
conf  = ConfigParser.ConfigParser()
conf.readfp(open(r'device.cfg'))
profile = conf.get('Device Config', 'profile')
ip = conf.get('Device Config','remote_ip')
port=conf.get('Device Config','remote_port')
send_freq = conf.get('Device Config', 'send_freq')
gnss_con = conf.get('GNSS', 'conn')
sensor_con = conf.get('Sensor','conn')

if gnss_con == 'yes':
    g_model = conf.get('GNSS', 'model')
    g_mode  = conf.get('GNSS', 'mode')
    g_port  = conf.get('GNSS', 'port')
    gnss    = getattr(dev_gnss, g_model+'_'+g_mode) 
    g = gnss()         
if sensor_con == 'yes':
    s_model = conf.get('Sensor','model')
    s_mode  = conf.get('Sensor','mode')
    sensor = getattr(dev_sensor, s_model+'_'+s_mode)
    s = sensor()
while 1:
    content = {}
    t, gcont = g.read(g_port)
    content.update(gcont)
    scont = s.read()
    content.update(scont)
    data = {"dev_id":mac,"prof_id":profile,"dev_time":t,"content":content}
    data = json.dumps(data)
    #print data
    c = pycurl.Curl()
    c.setopt(pycurl.URL, str(ip)+':'+str(port)+'/data/')
    c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, data)
    #c.setopt(pycurl.VERBOSE, 1)
    c.perform()
    c.close()
    time.sleep(int(send_freq))
