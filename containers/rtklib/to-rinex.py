from datetime import datetime
from importlib import import_module as imp
import time, ConfigParser, ast, sys, importlib, subprocess, os

cfg = ConfigParser.ConfigParser()
cfg.read('conf.cfg')

conf = cfg._sections["config"]
path = conf["path"]
rinex_ver = conf["rinex_ver"]
format_type = conf["format"]
meta = conf["meta"]

inp = path+"UIS01_78\:4b\:87\:a5\:9a\:ef/gnss/2017/130/" #temp testing path, function must be updated
out = inp+"rinex"
files = os.listdir(inp)
for f in files:
    t = str(datetime.now())
    filename = str(f)
    print "file", f
    f = inp+f
    a = './RTKLIB/app/convbin/gcc/convbin '+f+' -d '+out+' -r '+format_type
    print a
    p = subprocess.Popen(a, shell=True)
