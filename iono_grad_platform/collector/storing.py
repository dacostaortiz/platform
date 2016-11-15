from pymongo import MongoClient

#connects to mongodb
client = MongoClient()
#store data at database called "test"
db = client.test

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
