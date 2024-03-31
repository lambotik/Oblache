FROM python:alpine

WORKDIR ./usr/Oblache

RUN apk update && apk upgrade && apk add bash

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .