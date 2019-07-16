\set register_user `echo "$POSTGRES_REGISTER_USER"`
\set register_password `echo "$POSTGRES_REGISTER_PASSWORD"`

CREATE USER :register_user WITH ENCRYPTED PASSWORD :'register_password' ;

GRANT USAGE ON SCHEMA register TO :register_user;
GRANT ALL PRIVILEGES ON                  SCHEMA register TO :register_user;
GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA register TO :register_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA register TO :register_user;

