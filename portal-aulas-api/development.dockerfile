FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
COPY . .
COPY ./requirements.txt /requirements.txt
EXPOSE 8000
RUN pip install -r /requirements.txt
# RUN adduser -D user
# USER user
RUN python manage.py makemigrations
RUN python manage.py migrate
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]