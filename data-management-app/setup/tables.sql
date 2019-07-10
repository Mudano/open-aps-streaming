
CREATE TABLE openaps.app_users (
	id BIGSERIAL PRIMARY KEY,
	email VARCHAR,
	hashed_pw TEXT,
	verified BOOL,
	verification_code TEXT,
	admin BOOL DEFAULT FALSE,
	last_signin TIMESTAMP,
	login_count INTEGER,
	num_downloads INTEGER,
	total_download_size_mb NUMERIC,
	deactivated BOOLEAN,
	deactivated_date TIMESTAMP,
	created_ts TIMESTAMP
);
GRANT SELECT ON openaps.app_users TO admin_viewer;
GRANT USAGE, SELECT ON SEQUENCE openaps.app_users_id_seq TO ext_openaps_app;
GRANT SELECT, INSERT, DELETE ON TABLE openaps.app_users TO ext_openaps_app;


CREATE TABLE openaps.researcher_applications (

	seq_id BIGSERIAL PRIMARY KEY,
	researcher_name VARCHAR,
	email VARCHAR,
	phone_number VARCHAR,
	irb_approval TEXT,
	sponsor_organisation VARCHAR,
	oh_project_created BOOLEAN,
	request_description TEXT,
	application_processed BOOL,
	application_granted BOOL,
	processed_date TIMESTAMP,
	inserted_ts TIMESTAMP

);
GRANT SELECT ON openaps.researcher_applications TO admin_viewer;
GRANT USAGE, SELECT ON SEQUENCE openaps.researcher_applications_seq_id_seq TO ext_openaps_app;
GRANT SELECT, INSERT, UPDATE ON openaps.researcher_applications TO ext_openaps_app;

