# FROM python:3.10-alpine

# ENV PYTHONUNBUFFERED 1

# RUN mkdir /app
# WORKDIR /app
# COPY . .
# COPY ./requirements.txt /requirements.txt
# EXPOSE 8000
# RUN pip install -r /requirements.txt
# # RUN adduser -D user
# # USER user
# RUN python manage.py makemigrations
# RUN python manage.py migrate
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]

FROM python:3.10.2-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt