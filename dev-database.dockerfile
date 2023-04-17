FROM postgres:latest

ADD ./init-database-pg.sql /docker-entrypoint-initdb.d/

ENV PORT=5432
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=postgres

EXPOSE $PORT