# Dockerfile for machine learning tasks

FROM golemfactory/base:1.2

MAINTAINER Jacek Karwowski <jacek@golem.network>
# TODO maybe it should go to /usr/local?
# probably not to /opt/, see https://unix.stackexchange.com/questions/11544/what-is-the-difference-between-opt-and-usr-local

ENV ANACONDA_URL https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh

RUN mkdir /golem/dependencies && 
	cd /tmp &&
	wget ${ANACONDA_URL} -O ./anaconda.sh &&
	chmod +x anaconda.sh &&
	./anaconda.sh -b -p /golem/dependencies/anaconda3

ENV PATH=/golem/dependencies/anaconda3/bin:$PATH ANACONDA_ROOT=/golem/dependencies/anaconda3

