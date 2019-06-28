\set register_password `echo "$POSTGRES_REGISTER_PASSWORD"`
CREATE USER registration_app WITH ENCRYPTED PASSWORD :'register_password' ;

