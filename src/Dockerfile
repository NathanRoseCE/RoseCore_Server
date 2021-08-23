FROM python:3.8.3-alpine
# set default environment variables
ENV PYTHONUNBUFFERED 1

# pull official base image
FROM python:3.8.3-alpine

# set work directory
RUN mkdir /RoseCore
WORKDIR /RoseCore

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive 

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .