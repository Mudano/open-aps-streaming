\set register_user `echo "$POSTGRES_REGISTER_USER"`
\set register_password `echo "$POSTGRES_REGISTER_PASSWORD"`

CREATE USER :register_user WITH ENCRYPTED PASSWORD :'register_password' ;

