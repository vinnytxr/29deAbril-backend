# construir as imagens para os containers
build:
	docker-compose down
	docker-compose rm
	docker-compose build --no-cache

# configurar e construir/startar o ambiente dev
start:
	cp .env.dev .env
	docker-compose down
	docker-compose up -d db 
	sleep 3.0
	docker-compose up api

# restaura todo o ambiente dev (todos os dados são apagados inclusive do banco e o ambiente todo é reconstruido)
resolve: 
	sudo rm -rf ./postgres-data
	sudo rm -rf ./portal-aulas-api/media/*
	mkdir ./postgres-data
	docker rm -f portal-aulas-api
	docker rm -f portal-aulas-database
	docker rmi -f portal-aulas-api:1.0
	docker rmi -f portal-aulas-database
	make build
	make start

# para instanciar e startar manualmente cada container
api:
	cp .env.dev .env
	docker-compose up api

db:
	docker-compose up db

makemigrate:
	docker exec -it portal-aulas-api sh -c "python /app/manage.py makemigrations && python /app/manage.py migrate"

makemigrate_merge:
	docker exec -it portal-aulas-api sh -c "python /app/manage.py makemigrations --merge && python /app/manage.py migrate"

