#!/bin/bash
# chmod +x shell/deploy.sh
# use example:
# ./shell/deploy.sh user1@123.45.678.910

if [ $# -ne 1 ]; then
    echo "Usage: $0 <server-conection>"
    echo "Ex: $0 user1@123.45.678.910"
    exit 1
fi

server_conn=$1

echo "Deploying on $server_conn at /root/alessandro/29-april-backend"
rsync -avz --exclude="postgres-data" --exclude="portal-aulas-api/media" --exclude="shell" --exclude=".env" --exclude=".env.dev" --exclude=".env.prod" --exclude=".git" --exclude="portal-aulas-api/env" --delete . $server_conn:/root/alessandro/29-april-backend
echo "Deploy concluído!"