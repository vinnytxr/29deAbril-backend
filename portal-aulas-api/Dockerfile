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

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app
WORKDIR /app

# install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY . /app/
RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
