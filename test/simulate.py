import random
import json
import os, binascii
import sys
sys.path.insert(0, '../iono_grad_platform/collector/')
from storing import storing
from datetime import datetime
a= { 
    "dev_id" : "00:93:DA:01:2F:30", 
    "prof_id" : "bus",    
    "dev_time" : "2016-10-30, 11:24:31",    
    "content" : {
        "alt": "980",
        "lon": "34.3245",
        "lat":  "7.34355",
        "TD" : "24.9",
        "HR" : "5.2",
        "PR" : "990"}
}
s = storing() #connects to database
profiles = s.load_profiles()
prof_names = []
prof_idx = []
for idx, p in enumerate(profiles):
    prof_idx.append(idx)   
    prof_names.append(p.get("prof_id"))

b = random.random()
print a.keys()
print profiles
print ""
print ""
print prof_names

class simulate():
    def simu_cont(self,fields):
        content={}
        for f in fields:
            if f == "TD":
                TD = random.uniform(18,30)
                content.update({"TD":TD})
            elif f == "HR":
                HR = random.uniform(3.5,7)
                content.update({"HR":HR})
            elif f == "PR":
                PR = random.uniform(980,1020)
                content.update({"PR":PR})
            elif f == "alt":
                alt = 973.234
                content.update({"alt":alt})
            elif f == "lon":
                lon = -73.13958
                content.update({"lon":lon})
            elif f == "lat":
                lat = 7.1490436
                content.update({"lat":lat})
        return content
    
    def simu_data(self, data):
        ##
        if data.get("dev_id") is None:
            d = "" #generate a random MAC
            for i in range(6):
                if d == "":
                    d = d+binascii.b2a_hex(os.urandom(1))
                else:
                    d = d+":"+binascii.b2a_hex(os.urandom(1))
            data.update({"dev_id": d})
        
        if data.get("prof_id") is None:
            p = random.choice(prof_names)
            data.update({"prof_id": p})
        
        if data.get("dev_time") is None:
            t = str(datetime.now())
            data.update({"dev_time": t})
        
        if data.get("content") is None:
            if p in prof_names:
                idx = prof_names.index(p)
                fields = profiles[idx].get("fields")
            c = self.simu_cont(fields)
            data.update({"content": c})
            
        r = str(datetime.now())
        data.update({"rec_time": r})
        return data
        
    def simu_prof(self, prof):
        prof = {}
        return prof 

    def simu_dev(self, device):
        device = {}
        return device
		
#a = {}
#print simulate().simu_data(a)
