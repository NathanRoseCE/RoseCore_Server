# pull official base image
FROM python:3.8.3-alpine

# set work directory
RUN mkdir /usr/src/rosecore
WORKDIR /usr/src/rosecore

# make backup dir
RUN mkdir /usr/src/rosecore/backups/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
    
# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8000

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .


# run entrypoint.sh
ENTRYPOINT ["/usr/src/rosecore/entrypoint.sh"]