#! /bin/bash
/usr/bin/mongod &
cd /workspace/platform
python manage.py runserver 0.0.0.0:8088  
