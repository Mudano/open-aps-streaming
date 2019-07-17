\set nightscout_user `echo "$POSTGRES_NIGHTSCOUT_USER"`
\set nightscout_password `echo "$POSTGRES_NIGHTSCOUT_PASSWORD"`
\set register_user `echo "$POSTGRES_REGISTER_USER"`

CREATE USER :nightscout_user WITH ENCRYPTED PASSWORD :'nightscout_password' ;

GRANT USAGE ON SCHEMA ns_ingest TO :nightscout_user;
GRANT ALL PRIVILEGES ON                  SCHEMA ns_ingest TO :nightscout_user;
GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA ns_ingest TO :nightscout_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ns_ingest TO :nightscout_user;

GRANT USAGE ON SCHEMA register TO :nightscout_user;
ALTER DEFAULT PRIVILEGES FOR USER :register_user IN SCHEMA register grant SELECT, UPDATE ON tables TO :nightscout_user;
ALTER DEFAULT PRIVILEGES FOR USER :register_user IN SCHEMA register grant SELECT, UPDATE ON sequences TO :nightscout_user;

ALTER ROLE :nightscout_user SET search_path = 'ns_ingest'

