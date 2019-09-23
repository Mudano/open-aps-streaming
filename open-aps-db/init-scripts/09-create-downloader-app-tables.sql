
CREATE TABLE openaps.app_users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR,
  hashed_pw TEXT,
  verified BOOL,
  verification_code TEXT,
  admin BOOL DEFAULT FALSE,
  allowed_projects INT,
  last_signin TIMESTAMP,
  login_count INTEGER,
  num_downloads INTEGER,
  total_download_size_mb NUMERIC,
  deactivated BOOLEAN,
  deactivated_date TIMESTAMP,
  created_ts TIMESTAMP,
  UNIQUE(email)
);

GRANT SELECT ON openaps.app_users TO admin_viewer;
GRANT USAGE, SELECT ON SEQUENCE openaps.app_users_id_seq TO ext_openaps_app;
GRANT SELECT, INSERT, DELETE, UPDATE ON TABLE openaps.app_users TO ext_openaps_app;


CREATE TABLE openaps.researcher_applications (
  seq_id BIGSERIAL PRIMARY KEY,
  researcher_name VARCHAR,
  email VARCHAR,
  phone_number VARCHAR,
  project_requests INT,
  irb_approval TEXT,
  sponsor_organisation VARCHAR,
  request_description TEXT,
  application_processed BOOL,
  application_granted BOOL,
  processed_date TIMESTAMP,
  inserted_ts TIMESTAMP,
  UNIQUE(email)
);

GRANT SELECT ON openaps.researcher_applications TO admin_viewer;
GRANT USAGE, SELECT ON SEQUENCE openaps.researcher_applications_seq_id_seq TO ext_openaps_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON openaps.researcher_applications TO ext_openaps_app;

-- create the default application admin user
\set default_password_hash `echo "$DOWNLOADER_ADMIN_PASSWORD_HASH"`

INSERT INTO openaps.app_users
(email, hashed_pw, verified, verification_code, admin, created_ts, last_signin, login_count, num_downloads, total_download_size_mb, deactivated)
VALUES
('openaps.app@gmail.com', :'default_password_hash', TRUE, 'M3EM32O', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0, 0, 0, FALSE);


