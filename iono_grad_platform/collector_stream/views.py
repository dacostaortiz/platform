from django.shortcuts import render

# Create your views here.

from rest_framework_mongoengine.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from storing import store_stream
#from HttpRequest import *
#from models import *

#@csrf_exempt
@api_view(['GET','POST'])
def postdata(request):
    print "request", request
    print "method", request.method, "D:"
    if request.method == 'POST':
        #get data from the request and insert the record
        print request.POST
        print "antes err"
        print "imprimiendo: ",request.POST.get('dev_id')
        print "post err"
        #dev_id = request.POST["dev_id"]
        dev_id = request.POST.get("dev_id")
        #prof_id = request.POST["prof_id"]
        prof_id = request.POST.get("prof_id")
        #dev_time = request.POST["dev_time"]
        dev_time = request.POST.get("dev_time")
        rec_time = str(datetime.now())
        #content = request.POST["content"]
        content = request.POST.get("content")
        try:
		    s = store_stream()
		    s.insert_data({"dev_id": dev_id, "prof_id": prof_id, "dev_time": dev_time, "rec_time": rec_time, "content": content})
        except:
            return Response({ "ok": "false" })
        return Response({ "ok": "true" })

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
