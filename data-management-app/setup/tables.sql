
CREATE TABLE openaps.app_users (
	id BIGSERIAL PRIMARY KEY,
	email VARCHAR,
	hashed_pw TEXT,
	verified BOOL,
	verification_code TEXT,
	admin BOOL DEFAULT FALSE,
	created_ts TIMESTAMP
);
GRANT SELECT ON openaps.app_users TO admin_viewer;
GRANT USAGE, SELECT ON SEQUENCE openaps.app_users_id_seq TO ext_openaps_app;
GRANT SELECT, INSERT, DELETE ON TABLE openaps.app_users TO ext_openaps_app;
