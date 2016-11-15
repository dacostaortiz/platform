import subprocess
import json
from simulate import simulate
import random

x = simulate()

class test():

    def testData(self, data): #data is a dict, it could be void
        data = x.simu_data(data) 
        data = json.dumps(data)
        process = subprocess.Popen("echo '"+data+"' > out.txt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = subprocess.Popen("http --verbose POST localhost:8000/data/ < out.txt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        out, err = process.communicate()
        if(process.returncode==0):
            print out
        else:
            print err
            
    def testDev(self):
        dev = x.simu_dev({}) 
        process = subprocess.Popen("echo '"+json.dumps(dev)+"' > out.txt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = subprocess.Popen("http --verbose POST localhost:8000/dev/ < out.txt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        out, err = process.communicate()
        if(process.returncode==0):
            print out
        else:
            print err
        return dev
            
t = test()
for i in range(2):
    dev = t.testDev() #simulate 2 devices and sends it to the platform

for i in range(15):
    data = {}
    t.testData(data) #simulate measures without profiles from the registered devices

for i in range(3):
    dev = t.testDev() #simulate 3 devices
    prof_ids = ["bus","drone"]
    prof_id = random.choice(prof_ids)
    for j in range(10):
        data = {"dev_id":dev.get("dev_id"),"prof_id":prof_id} 
        t.testData(data) #simulate 10 measures from each of the 3 devices
    
for i in range(1):
    dev = t.testDev() #simulate a device
    prof_ids = ["bus","drone"]
    prof_id = random.choice(prof_ids)
    for j in range(10):
        data = {"dev_id":dev.get("dev_id"),"prof_id":prof_id,"check":0} 
        t.testData(data) #simulated measures will not have some fields in the content
    
