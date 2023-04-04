build:
	docker-compose down
	docker-compose rm
	docker-compose build --no-cache

start:
	cp .env.dev .env
	docker-compose down
	docker-compose up -d db
	docker-compose up web

