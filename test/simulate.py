import random
import json
import os, binascii
import sys
sys.path.insert(0, '../iono_grad_platform/collector/')
from storing import storing
from datetime import datetime

s = storing() #connects to database
profiles = s.load_profiles()
prof_names = []
prof_idx = []
for idx, p in enumerate(profiles):
    prof_idx.append(idx)   
    prof_names.append(p.get("prof_id"))

devices = s.load_devices()
dev_ids = []
dev_idx = []
for idx, d in enumerate(devices):
	dev_idx.append(idx)
	dev_ids.append(d.get("dev_id"))

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
        if data.get("dev_id") is None:
            #gets a device retrieved from the db
            d = random.choice(dev_ids) 
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
    
    
    def simu_info(self):
        info = {}
        groups = ["UIS","Metrolinea"]
        if random.random() >= 0.7:
            g = None
        else:
            g = random.choice(groups)
        p = {"alt":973.234,"lon":-73.13958,"lat":7.1490436}
        d = "simulated device"
        info.update({"dev_group": g,"pos":p,"description":d})
        return info


    def simu_dev(self, device):
        groups = ["UIS","Metrolinea"]
        if device.get("dev_id") is None:
            d = "" #generate a random MAC
            for i in range(6):
                if d == "":  
                    d = d+binascii.b2a_hex(os.urandom(1))
                else:
                    d = d+":"+binascii.b2a_hex(os.urandom(1))
            device.update({"dev_id": d})

        if device.get("timestamp") is None:
            t = str(datetime.now())
            device.update({"timestamp":t})
        
        if device.get("info") is None:
            i = self.simu_info()
            device.update({"info":i})
        else:
            info = device.get("info")
            if info.get("dev_group") is None:
                if random.random() >= 0.7:
                    g = None
                else:
                    g = random.choice(groups)
                info.update({"dev_group":g})
                device.update({"info": info})
        return device
