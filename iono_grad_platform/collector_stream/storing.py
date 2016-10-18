from pymongo import MongoClient

client = MongoClient()
db = client.test

class store_stream():
	
    def insert_data(self,data):
        insert = db.test.insert_one(data)
        print insert.inserted_id
		
