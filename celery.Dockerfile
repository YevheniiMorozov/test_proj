FROM python:3.10-slim AS builder

COPY . .
COPY ./creds.json .

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR false
RUN pip install --upgrade pip
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y python3 python3-dev gcc \
    gfortran musl-dev g++ libffi-dev libxml2 \
    libxml2-dev libxslt-dev libc-dev libffi-dev

RUN pip install -r requirements.txt