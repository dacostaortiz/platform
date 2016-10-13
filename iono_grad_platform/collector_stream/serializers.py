from models import *
from rest_framework import serializers as drf_serializer
from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework_mongoengine.validators import UniqueValidator

class DeviceSerializer(DocumentSerializer):
    dev_id = drf_serializer.CharField(validators=[UniqueValidator(Device.objects.all())])    
    class Meta:
        model = Device
        #depth = 2


class ProfileSerializer(DocumentSerializer):
    
    class Meta:
        model = Profile
        

class Post_prof_Serializer(DocumentSerializer):
    
    class Meta:
        model = Post_prof


class Post_stream_Serializer(DocumentSerializer):
    
    class Meta:
        model = Post_stream
        depth = 2
