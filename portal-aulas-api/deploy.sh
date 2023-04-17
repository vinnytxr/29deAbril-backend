pathctl="/home/alessandro/.fly/bin"
cp ../.env.prod ./.env
${pathctl}/flyctl auth logout
${pathctl}/flyctl auth login
${pathctl}/flyctl deploy