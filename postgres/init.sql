CREATE DATABASE photos;

BEGIN;

CREATE USER photo WITH
  LOGIN
  SUPERUSER
  INHERIT
  NOCREATEDB
  CREATEROLE
  NOREPLICATION
  PASSWORD 'password';

ALTER ROLE photo SET client_encoding TO 'utf8';
ALTER ROLE photo SET default_transaction_isolation TO 'read committed';
ALTER ROLE photo SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE photos TO photo;

CREATE ROLE administrators;
CREATE ROLE authenticated;
CREATE ROLE unauthenticated;
CREATE ROLE anonymous;

GRANT authenticated, unauthenticated TO administrators;
GRANT unauthenticated TO anonymous;

GRANT SELECT ON pg_authid TO PUBLIC;

COMMIT;