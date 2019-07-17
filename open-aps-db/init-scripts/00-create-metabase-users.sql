\set metabase_password `echo "$POSTGRES_METABASE_PASSWORD"`
CREATE USER openapsuser WITH ENCRYPTED PASSWORD :'metabase_password';
CREATE USER rdsadmin WITH ENCRYPTED PASSWORD :'metabase_password';
 
