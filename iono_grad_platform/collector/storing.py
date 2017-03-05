from pymongo import MongoClient
from checksum import checksum
import ConfigParser
import os

conf = ConfigParser.ConfigParser()
conf.readfp(open(r'config.cfg'))
ip		= conf.get('Mongo', 'ip')
port	= conf.get('Mongo', 'port')
name	= conf.get('Mongo', 'name')
route	= conf.get('Mongo', 'route')
#connects to mongodb
client = MongoClient(host=[str(ip)+':'+str(port)])
#store data at database called "test"
db = client[name]

class storing():

    def insert_data(self,data):
        #insert data into a collection called "data"
        insert = db.data.insert_one(data)
        print "Data inserted at: ", insert.inserted_id
        
    def insert_profile(self,profile):
        #insert data into a collection called "profile"
        insert = db.profile.insert_one(profile)
        print "Profile inserted at: ", insert.inserted_id

    def load_profiles(self):
        profiles = []
        for p in db.profile.find():
            profiles.append(p)
        return profiles

    def insert_device(self, device):
        #insert data into a collection called "device"
        insert = db.device.insert_one(device)
        print "Device inserted at: ", insert.inserted_id

    def load_devices(self):
        devices = []
        for d in db.device.find():
            devices.append(d)
        return devices
        
    def insert_batch(self, meta):
		#inserts the metadata related to each uploaded file in batch mode
		insert = db.meta.insert_one(meta)
		print "Metadata inserted at: ", insert.inserted_id

    def handle_file(self,f,dev_id):
		#stores each uploaded file in the file system
        r = self.check_destiny(f)
        with open(r+f.name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
        chksum = checksum(r+f.name)
        return chksum
    
    def check_destiny(self,f):
		#checks the regular expression and creates directory if necessary
        name = str(f)
        nick =  str(name[0:5])
        mac =   str(name[6:23])
        mtype = str(name[24:28])
        year =  str(str(20)+name[28:30])
        day =   str(name[30:33])
        if os.path.isdir(route+nick+'_'+mac):
            r = route+nick+'_'+mac+'/'
            if os.path.isdir(r+mtype):
                r = r+mtype+'/'
                if os.path.isdir(r+year):
                    r = r+year+'/'
                    if os.path.isdir(r+day):
                        r =  r+day
                        return r+'/'
                    else:
                        r = r+day
                        os.makedirs(r)
                        return r+'/'
                else:
                    r = r+year+'/'+day
                    os.makedirs(r)
                    return r+'/'
            else:
                r = r+mtype+'/'+year+'/'+day
                os.makedirs(r)
                return r+'/'
        else:
            r = route+nick+'_'+mac+'/'+mtype+'/'+year+'/'+day
            os.makedirs(r)
            return r+'/'
