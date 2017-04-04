import sys, os, psutil, ast, ConfigParser, time
from importlib import import_module as imp
sys.path.insert(0,'./sensors/')

conf = ConfigParser.ConfigParser()
conf.read('batch2.cfg')
dev_conf    = conf._sections["Device Config"]
num_sensors = dev_conf["num_sensors"]

sensors = []
for i in range(int(num_sensors)):
    s_conf  = conf._sections["Sensor"+str(i+1)]
    model   = s_conf["model"]
    mode    = s_conf["mode"]
    init    = ast.literal_eval(s_conf["init"])
    sensors.append(getattr(imp(model),mode)(**init))

for s in sensors:
    print s
    s.start()

while 1:
    for s in sensors:
        s.is_alive()
    time.sleep(600)

    time.sleep(15)
