pathctl="/home/alessandro/.fly/bin"
cp ../.env.prod ./.env
${pathctl}/flyctl deploy

# /home/alessandro/.fly/bin/flyctl auth logout