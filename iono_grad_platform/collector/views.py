from django.shortcuts import render

# Create your views here.

from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from storing import storing
import json
from django.http import HttpResponse

s = storing() #connects to database
profiles = s.load_profiles()

prof_names = []
prof_idx = []
for idx, p in enumerate(profiles):
    prof_idx.append(idx)   
    prof_names.append(p.get("prof_id")) #list of names of the profiles' id


def index(request):
    return HttpResponse('<h1>Welcome</h1> Now the server is running. Please post your data to "localhost:8000/post/".')

@api_view(['GET','POST'])
def sendData(request):   
    if request.method == 'POST': #get data from the request
        body = request.data
        dev_id = body.get("dev_id")
        prof_id = body.get("prof_id")
        dev_time = body.get("dev_time")
        rec_time = str(datetime.now())
        content = body.get("content")
        if prof_id in prof_names:
            idx = prof_names.index(prof_id)
            cont_fields = content.keys()
            fields = profiles[idx].get("fields")
            if set(cont_fields).intersection(fields) == set(fields):
                chk = 1 #"satisfied"
            else:
                chk = 0 #"not satisfied"
        else:
            chk = 2 #"profile doesn't exist"
        if dev_id is not None:
            try: #insert data on the mongo database
                s.insert_data({"dev_id": dev_id, "prof_id": prof_id, "dev_time": dev_time, "rec_time": rec_time, "content": content, "check": chk})
            except:
                if content is None:
                    print "not content dict, please check this field" #this message could be sent to a log error file.
                return Response({ "ok": "false" })
        else:
            print "No device id"
            return Response({ "ok": "false" })
        return Response({ "ok": "true" })

    if request.method == 'GET':
        return Response({"ok":"true"})

@api_view(['GET','POST'])
def sendProfile(request):
    if request.method == 'POST':
        body = request.data
        prof_id = body.get("prof_id")
        fields  = body.get("fields")
        desc    = body.get("description")
        if prof_id in prof_names:
            print "this profile already exists"
            return Response({"ok":"false"})
        try:
            p = {"prof_id": prof_id, "fields": fields, "description": desc}
            s.insert_profile(p)
            profiles.append(p) 
            idx = max(prof_idx)
            prof_idx.append(int(idx)+1)
            prof_names.append(prof_id)
        except:
            return Response({ "ok": "false" })
        return Response({ "ok": "true" })

@api_view(['GET','POST'])
def sendDevice(request):
    if request.method == 'POST':
        body = request.data
        dev_id = body.get("dev_id")
        dev_time = body.get("dev_time")
        rec_time = str(datetime.now())
        info = body.get("info")
        try:
            s.insert_device({"dev_id": dev_id, "dev_time": dev_time, "rec_time": rec_time, "info": info})
        except:
            return Response({ "ok": "false" })
        return Response({ "ok" : "true" })
