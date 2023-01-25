FROM python:3.10.7
ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir /app
WORKDIR /app

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y nano

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY /dental_app .