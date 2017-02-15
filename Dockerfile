From ubuntu:16.04
MAINTAINER Diego Acosta <dacostaortiz@outlook.com>

EXPOSE 8088

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
RUN echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.4.list 
RUN apt-get update && apt-get install -y --no-install-recommends \
	python-dev \ 
	python-pip \
	mongodb-org \
	git \
	vim \
	build-essential 
RUN pip install --upgrade pip
RUN pip install django djangorestframework pymongo
WORKDIR /workspace
RUN mkdir -p /data/db
EXPOSE 27017
RUN git clone https://github.com/dacostaortiz/platform.git
WORKDIR /workspace/platform
COPY config.cfg .
COPY run.sh .
