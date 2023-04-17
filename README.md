# Portal de Aulas Online (backend)
### Instruções gerais para startar o projeto em ambiente de desenvolvimento
#### 1- Configurar o arquivo `.env.dev` com as credências de acesso ao database e porta do servidor do seu host, como no exemplo a seguir:
```
DEBUG=1
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=portal_aulas_online
SQL_USER=root
SQL_PASSWORD=root
SQL_HOST=db
SQL_PORT=5432
```
**OBS:** Caso utilize docker, basta utilizar as credênciais pré-estabelecidas no `.env.dev`

#### 2- Construir ambiente (utilizando docker):
(estando na raiz do projeto):
- `make start` irá rodar todos os comandos do docker-compose para instanciar o banco de dados `localhost:5432` e a aplicação backend `localhost:8080`

### Comandos uteis
(estando na raiz do projeto):
- `make resolve` irá reconstruir todo o ambiente de desenvolvimento, **todos os dados serão apagados**, incluindo do banco de dados e as migrations serão executadas novamente (usar quando obtiver algum erro de configuração)
- `make api` irá instanciar e startar apenas o container para a api
- `make db` irá instanciar e startar apenas o container para o database
- `make build` irá apenas construir as imagens de docker para a api e database

### Credênciais Servidor de Produção
##### Database (PostgreSQL):
`postgres://postgres:sjBrPulEjnGxPcB@alens-pg-database.fly.dev:5432/postgres`
<br/>
`jdbc:postgresql://alens-pg-database.fly.dev:5432/postgres`
##### API: 
`https://portal-aulas-api.fly.dev/`


### Outros Links
#### [Modelo Banco de Dandos](https://dbdiagram.io/d/642a4d435758ac5f17262b1e)
#### [Repositório Frontend](https://github.com/349Team/portal-aulas-online-frontend)