from pymongo import MongoClient

#connects to mongodb
client = MongoClient()
#store data at database called "streamdb"
db = client.streamdb

class store_stream():
	
    def insert_data(self,data):
        #inset data into a collection called "post"
        insert = db.post.insert_one(data)
        print "Data inserted at: ", insert.inserted_id
		
