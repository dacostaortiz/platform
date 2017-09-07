From ubuntu:16.04
MAINTAINER Diego Acosta <dacostaortiz@outlook.com>

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
	python-dev \ 
	python-pip \
	git \
	vim \
	build-essential 
RUN pip install --upgrade pip
RUN pip install -U setuptools
RUN pip install configparser importlib pyutillib subprocess32
RUN mkdir -p /workspace
WORKDIR /workspace

RUN git clone https://github.com/tomojitakasu/RTKLIB.git
RUN make -C /workspace/RTKLIB/app/convbin/gcc/

COPY conf.cfg .
COPY to-rinex.py .


