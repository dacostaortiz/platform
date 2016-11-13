import subprocess
import json
from simulate import simulate

x = simulate()

class test():
    def testData(self):
        data = x.simu_data({}) 
        data = json.dumps(data)
        process = subprocess.Popen("echo '"+data+"' > out.txt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #process = subprocess.Popen("http --verbose POST localhost:8000/data/ '"+x+"'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = subprocess.Popen("http --verbose POST localhost:8000/data/ < out.txt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        out, err = process.communicate()
        if(process.returncode==0):
            print out
        else:
            print err
            
    def testDev(self):
        dev = x.simu_dev({}) 
        dev = json.dumps(dev)
        process = subprocess.Popen("echo '"+dev+"' > out.txt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = subprocess.Popen("http --verbose POST localhost:8000/dev/ < out.txt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        out, err = process.communicate()
        if(process.returncode==0):
            print out
        else:
            print err
t = test()
for i in range(50):
    t.testData()
#t.testDev()
