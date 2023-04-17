CREATE EXTENSION dblink;
SELECT 'CREATE DATABASE portal_aulas_online'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'portal_aulas_online')\gexec