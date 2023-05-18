# FROM python:3.10-alpine

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Install system dependencies
# RUN apk update \
#     && apk add --no-cache libstdc++ libgcc libx11 glib \
#     && rm -rf /var/cache/apk/*

# RUN mkdir -p /app
# WORKDIR /app

# COPY requirements.txt /tmp/requirements.txt
# RUN set -ex && \
#     pip install --upgrade pip && \
#     pip install -r /tmp/requirements.txt && \
#     rm -rf /root/.cache/

# COPY . /app/
# RUN python manage.py makemigrations

# EXPOSE 8080
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]


FROM python:3.10.2-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY . /app/
RUN python manage.py makemigrations

EXPOSE 8080
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]