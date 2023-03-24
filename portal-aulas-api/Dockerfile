# FROM python:3.10-alpine

# ENV PYTHONUNBUFFERED 1

# RUN mkdir /api
# WORKDIR /api
# COPY . .
# COPY ./requirements.txt /requirements.txt
# EXPOSE 8000
# RUN pip install -r /requirements.txt
# RUN adduser -D user
# USER user
# RUN python manage.py makemigrations
# RUN python manage.py migrate

# pull official base image
FROM python:3.10-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create the app directory - and switch to it
RUN mkdir -p /app
WORKDIR /app

# install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

# copy project
COPY . /app/

# expose port 8000
EXPOSE 8000
RUN python manage.py makemigrations
RUN python manage.py migrate
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]