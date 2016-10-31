from pymongo import MongoClient

#connects to mongodb
client = MongoClient()
#store data at database called "streamdb"
db = client.streamdb

class storing():
	
    def insert_data(self,data):
        #insert data into a collection called "post"
        insert = db.post.insert_one(data)
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
