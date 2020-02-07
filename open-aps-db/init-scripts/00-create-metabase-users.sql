\set metabase_password `echo "$METABASE_PASSWORD"`
CREATE USER openapsuser WITH ENCRYPTED PASSWORD :'metabase_password';
GRANT openapsuser to open_aps_admin;

