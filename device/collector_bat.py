from datetime import datetime
import time
import ConfigParser
import uuid
import pycurl
import StringIO
from utils import *
import os
import shutil

mac_num = hex(uuid.getnode()).replace('0x','')
mac     = ':'.join(mac_num[i : i + 2] for i in range(0,11,2))

conf = ConfigParser.ConfigParser()
conf.readfp(open(r'device2.cfg'))
name        = conf.get('Device Config', 'name')
profile     = conf.get('Device Config', 'profile')
ip          = conf.get('Device Config', 'remote_ip')
port        = conf.get('Device Config', 'remote_port')
send_freq   = conf.get('Device Config', 'send_freq')
path        = conf.get('Batch',         'path')
print path

while 1:
    #check if exist file on folder
    chk = exist_file(path)
    if chk == True:
        files = os.listdir(path)
        for f in files:
            t = str(datetime.now())
            filename = str(f)
            print "file", f
            f = path+f
            ch = checksum(f)
            fields = [('dev_id',    name+'_'+mac),
                      ('profile',   profile),
                      ('dev_time',  t),
                      ('chksum',    str(ch)),
                      ('filename', filename),
                      ('raw', (pycurl.FORM_FILE, f))]
            response = StringIO.StringIO()
            c = pycurl.Curl()
            c.setopt(pycurl.URL, str(ip)+':'+str(port)+'/batch/')
            c.setopt(pycurl.HTTPPOST, fields)
            c.setopt(pycurl.VERBOSE, 1)
            c.setopt(pycurl.WRITEFUNCTION, response.write) #write response
            c.perform()
            c.close()
            resp = response.getvalue()
            if resp == r'{"ok":"true"}':
                print "moving file"
                shutil.move( f, path+'../sent/' )
            else:
                print "checksum invalid, should send file again"
    else:
        print "empty directory, not sending anything"
    
    time.sleep(int(send_freq))
