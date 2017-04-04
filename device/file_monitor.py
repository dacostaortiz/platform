from datetime import datetime
import time, ConfigParser, uuid, pycurl, StringIO, os, shutil
from utils import *

mac_num = hex(uuid.getnode()).replace('0x','')
mac     = ':'.join(mac_num[i : i + 2] for i in range(0,11,2))

conf = ConfigParser.ConfigParser()
conf.read('batch.cfg')
dev_conf    = conf._sections["Device Config"]
name        = dev_conf["name"]
profile     = dev_conf["profile"]
ip          = dev_conf["remote_ip"]
port        = dev_conf["remote_port"]
send_freq   = dev_conf["send_freq"]
data_dir    = dev_conf["data_dir"]

incoming    = data_dir+'incoming/'
send_queue  = data_dir+'send_queue/'
sent        = data_dir+'sent/'

pidfile     = open('/var/run/file_monitor.pid', 'w')
pidfile.write(str(os.getpid()))
pidfile.close()

while 1:
    #check if exist file on folder
    chk = exist_file(send_queue)
    if chk == True:
        files = os.listdir(send_queue)
        for f in files:
            t = str(datetime.now())
            filename = str(f)
            print "file", f
            f = send_queue+f
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
                shutil.move( f, sent)
            else:
                print "checksum invalid, should send file again"
    else:
        print "empty directory, not sending anything"
    
    time.sleep(int(send_freq))
