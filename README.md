Ionospherical Gradients Detection Platform
==========================================

On this repository relies the source code of the platform for ionospherical gradients detection.


## Dependencies

* Python      >=  2.7
* Mongodb     >=  3.2
* Django      >=  1.8
* djangorestframework >=  2.0 
* PyMongo     >=  3.0

## Installation

First we install pip and [mongo db](https://docs.mongodb.com/manual/installation/)

Then we create a virtual enviroment in order to avoid to mess up our system. 
```bash
$ virtualenv env
$ source env/bin/activate
```
After that we install our dependencies
```bash
$ pip install django
$ pip install djangorestframework
$ pip install pymongo

```
Now we are ready to run our test server.


## Usage

First we start our mongodb service, it could be used by default at localhost:27017
Then we source our virtual enviroment and finally we start our server.
```bash
$ sudo service mongod start
$ source env/bin/activate
$ python manage.py runserver
```

Now we can post our data to the following url "localhost:8000/data/"
For example, let's post a sample json file of a remote station.
Using httpie:
```bash
http POST localhost:8000/data/ < sample.json    
```
Let's check the posted data.
```bash
$ mongo
> show databases
> use streamdb
> show collections
> db.data.find()
{ "_id" : ObjectId("5807403d0e2a290e7b94f950"), "dev_id" : "00:93:DA:01:2F:30", "dev_time" : "2016-10-19 09:43:25.843574", "rec_time" : "2016-11-11 10:15:42.857498", "prof_id" : "meteo", "content" : { "PR" : "965", "TD" : "23.2", "HR" : "5.1" } }
```
