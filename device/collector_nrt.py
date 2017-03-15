from datetime import datetime
from importlib import import_module as imp
import time, uuid, ConfigParser, pycurl, json, ast, sys, importlib
#import sensor
sys.path.insert(0,'./sensors/')

#device id must to be unique, we could use mac as id
mac_num = hex(uuid.getnode()).replace('0x','')
mac     = ':'.join(mac_num[i : i + 2] for i in range(0,11,2))

#load configurations
conf  = ConfigParser.ConfigParser()
conf.read('nrt.cfg')
dev_conf    = conf._sections["Device Config"]
profile     = dev_conf["profile"]
ip          = dev_conf["remote_ip"]
port        = dev_conf["remote_port"]
send_freq   = dev_conf["send_freq"]
num_sensors = dev_conf["num_sensors"]

#load sensors' drivers
sensors = []
for i in range(int(num_sensors)):
    s_conf  = conf._sections["Sensor"+str(i+1)]
    model   = s_conf["model"]
    mode    = s_conf["mode"]
    init    = ast.literal_eval(s_conf["init"])
    sensors.append(getattr(imp(model),mode)(**init))

print sensors

while 1:
    content = {}
    for s in sensors:
        content.update(s.read())
    t = str(datetime.now())
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
