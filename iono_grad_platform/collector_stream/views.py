from django.shortcuts import render

# Create your views here.

from rest_framework_mongoengine.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import *
#from models import *

class DeviceList(ListCreateAPIView):
    serializer_class = DeviceSerializer
    queryset = Device.objects.all()


class ProfileList(ListCreateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class Post_prof_List(ListCreateAPIView):
    serializer_class = Post_prof_Serializer
    queryset = Post_prof.objects.all()


class Post_stream(ListCreateAPIView):
    serializer_class = Post_stream_Serializer
    queryset = Post_stream.objects.all()

