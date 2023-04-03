build:
	docker-compose build --no-cache

all:
	docker-compose exec web python manage.py migrate
	docker-compose up --build db
	docker-compose up web