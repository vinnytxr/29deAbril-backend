FROM postgres:latest
ADD ./init-database-pg.sql /docker-entrypoint-initdb.d/
ENV PORT=5432
ENV POSTGRES_USER=root
ENV POSTGRES_PASSWORD=root
ENV POSTGRES_DB=root
EXPOSE $PORT