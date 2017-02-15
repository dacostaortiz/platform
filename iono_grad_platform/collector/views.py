from django.shortcuts import render

# Create your views here.

from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from storing import storing
import json
from django.http import HttpResponse
from forms import UploadBatchForm

s = storing() #connects to database
profiles = s.load_profiles()

prof_ids = []
prof_idx = []
for idx, p in enumerate(profiles):
    prof_idx.append(idx)   
    prof_ids.append(p.get("prof_id")) #list of names of the profiles' id


def index(request):
    return HttpResponse('<h1>Welcome</h1> Now the server is running. Please post your data to "http://cagepocs.sc3.uis.edu.co:8088/data/".')

@api_view(['GET','POST'])
def sendData(request):   
    if request.method == 'POST': #get data from the request
        body = request.data
        dev_id = body.get("dev_id")
        prof_id = body.get("prof_id")
        dev_time = body.get("dev_time")
        rec_time = str(datetime.now())
        content = body.get("content")
        if prof_id in prof_ids:
            idx = prof_ids.index(prof_id)
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
        if prof_id in prof_ids:
            print "this profile already exists"
            return Response({"ok":"false"})
        try:
            p = {"prof_id": prof_id, "fields": fields, "description": desc}
            s.insert_profile(p)
            profiles.append(p) 
            idx = max(prof_idx)
            print "idx", idx, prof_idx
            prof_idx.append(int(idx)+1)
            print "lel", prof_idx
            prof_ids.append(prof_id)
            print prof_ids
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
        
@api_view(['POST'])
def sendBatch(request):
	if request.method == 'POST':
		print request.POST
		print request.FILES
		form = UploadBatchForm(request.POST,request.FILES)
		if form.is_valid():
			print "file received"
			dev_id = request.POST.get("dev_id")
			prof_id = request.POST.get("profile")
			dev_time = request.POST.get("dev_time")
			rec_time = str(datetime.now())
			chksum_rec = request.POST.get("chksum")
			chksum_cal = s.handle_file(request.FILES['raw'],dev_id)
			s.insert_batch({"dev_id": dev_id, "prof_id": prof_id, 
			"dev_time": dev_time, "rec_time": rec_time, "checksum": chksum_rec})
			if chksum_rec == chksum_cal:
				return Response({"ok":"true"})
			else:
				return Response({"ok":"not valid checksum"})
		else:
			print "form no valid"
			return Response({"ok":"false"})
