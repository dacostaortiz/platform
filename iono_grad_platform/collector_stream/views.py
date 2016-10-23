from django.shortcuts import render

# Create your views here.

from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from storing import store_stream
import json
from django.http import HttpResponse

def index(request):
    return HttpResponse('<h1>Welcome</h1> Now the server is running. Please post your data to "localhost:8000/post/".')

@api_view(['GET','POST'])
def postdata(request):
    if request.method == 'POST':
        #get data from the request
        body = request.data
        #print body
        dev_id = body.get("dev_id")
        prof_id = body.get("prof_id")
        dev_time = body.get("dev_time")
        rec_time = str(datetime.now())
        content = body.get("content")
        try: #insert data on the mongo database
	    s = store_stream()
	    s.insert_data({"dev_id": dev_id, "prof_id": prof_id, "dev_time": dev_time, "rec_time": rec_time, "content": content})
        except:
            return Response({ "ok": "false" })
        return Response({ "ok": "true" })
