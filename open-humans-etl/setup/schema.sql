
CREATE SCHEMA openaps;

CREATE USER ingestor;
ALTER USER ingestor WITH PASSWORD '';
GRANT USAGE ON SCHEMA openaps TO ingestor;

CREATE USER admin_viewer;
ALTER USER admin_viewer WITH PASSWORD '';
GRANT USAGE ON SCHEMA openaps TO admin_viewer;
GRANT SELECT ON ALL TABLES IN SCHEMA openaps TO admin_viewer;

CREATE USER viewer;
ALTER USER viewer WITH PASSWORD '';
GRANT USAGE ON SCHEMA openaps TO viewer;

CREATE USER ext_openaps_app;
ALTER USER ext_openaps_app WITH PASSWORD '';
GRANT USAGE ON SCHEMA openaps TO ext_openaps_app;