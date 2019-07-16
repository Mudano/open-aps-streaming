Database Initialisation Scripts
======================================

This directory contains the raw SQL scripts that are used to initialise all elements of the application database, these scripts are handwritten and designed for security by using environment variables to specify any sensitive information (these environment variables should be provided in a `.env` file built form the `.env-template` file in the project root).

However, once metabase was added to the project to provide visualisation capabailities this solution couldn't be maintained for all database initialisation. Metabase stores all aspects of it's configuration in an accompanying application database, in this case a PostgreSQL database. This means that there is no way to make the initialisation of the metabase visualisations for this tool replicable (allowing for re-deployments of the tool if required) apart from by performing a dump of the metabase application database state via `pg_dump`. This provides a SQL file from which the metabase config can be re-initialised into an empty database if required.

Unfortunately, all aspects of metabase config are stored in this database dump, including metabase user names, emails, and hashed passwords. Given this personal information, the potential vulnerability of hashed passwords to cracking, and the nature of the application. It was decided that this initialisation script should not be stored alongside the rest of the SQL initialisation scripts in version control.

In this directory the file `1_metabase_db_definition.sql` is empty as stored in version control, this file would be the one used to initialise the metabase components of the database, as it is the application images should build and the application should run fine without any changes being made to this file, the only element that will not function is the metabase visualisations which will not exist.

The full version of the `1_metabase_db_definition.sql` file is held by the owners of this project (OpenAPS) and may be shared at their discretion. Whilst the SQL file is not included here this is largely precautionary, no explicitly sensitive information is believed to be stored in plaintext in the file.
 

