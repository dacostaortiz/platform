from __future__ import unicode_literals

from django.db import models
# Create your models here.
from mongoengine import * 
MONGO_DATABASE_NAME = 'streamdb'
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
connect(MONGO_DATABASE_NAME, host=MONGO_HOST, port=MONGO_PORT)


class Profile(Document):
    prof_id = StringField(max_length=50)


class Device(Document):
    dev_id = StringField(max_length=50)
    #profile = ReferenceField(Profile)
    profile = StringField(max_length=50)


class Post_prof(Document):
    author = ReferenceField(Device)
    profile = ReferenceField(Profile)


class Post_stream(Document):
    author = ReferenceField(Device)
    data = DictField()
    
