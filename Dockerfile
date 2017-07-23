FROM python:3.5-slim

MAINTAINER Sahand Hariri sahandha@gmail.com

RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*
RUN apt-get -qq update
RUN sudo apt-get -qq -y install software-properties-common

RUN sudo apt-get install -y python-pip 
Run pip install --upgrade pip 
Run pip install numpy 

RUN apt-get update
RUN apt-get install -yq default-jdk

RUN wget http://d3kbcqa49mib13.cloudfront.net/spark-2.0.2-bin-hadoop2.7.tgz 
RUN tar xvf spark-2.0.2-bin-hadoop2.7.tgz
RUN rm spark-2.0.2-bin-hadoop2.7.tgz
RUN mv spark-2.0.2-bin-hadoop2.7 /opt/spark
RUN pip install tornado

EXPOSE 8888

Add iso_server /external/TornadoWebServer


CMD ["python", "/external/TornadoWebServer/server.py"]
