
CREATE TABLE openaps.device_status (
  seq_id BIGSERIAL PRIMARY KEY,
  user_id INTEGER,
  id VARCHAR,
  device VARCHAR,
  pump_id VARCHAR,
  pump_bolusing BOOL,
  pump_suspended BOOL,
  pump_model VARCHAR,
  loop_cob NUMERIC,
  loop_iob NUMERIC,
  loop_version VARCHAR,
  loop_failure_reason TEXT,
  snooze VARCHAR,
  override_active BOOL,
  source_entity INTEGER,
  raw_json JSONB,
  created_at timestamp
);
GRANT SELECT ON TABLE openaps.device_status TO viewer;
GRANT SELECT ON TABLE openaps.device_status TO ext_openaps_app;
GRANT SELECT, INSERT ON TABLE openaps.device_status TO ingestor;


CREATE TABLE openaps.device_status_metrics (
  seq_id BIGSERIAL PRIMARY KEY,
  device_status_id VARCHAR,
  iob_iob NUMERIC,
  iob_activity NUMERIC,
  iob_basal_iob NUMERIC,
  iob_bolus_iob NUMERIC,
  iob_net_basal_insulin NUMERIC,
  iob_bolus_insulin NUMERIC,
  iob_timestamp TIMESTAMP,
  suggested_temp VARCHAR,
  suggested_bg NUMERIC,
  suggested_tick VARCHAR,
  suggested_eventual_bg NUMERIC,
  suggested_insulin_req NUMERIC,
  suggested_reservoir NUMERIC,
  suggested_cob NUMERIC,
  suggested_iob NUMERIC,
  enacted_temp VARCHAR,
  enacted_bg NUMERIC,
  enacted_tick VARCHAR,
  enacted_eventual_bg NUMERIC,
  enacted_insulin_req NUMERIC,
  enacted_reservoir VARCHAR,
  enacted_cob NUMERIC,
  enacted_iob NUMERIC,
  enacted_duration NUMERIC,
  enacted_rate NUMERIC,
  enacted_timestamp TIMESTAMP
);
GRANT SELECT ON TABLE openaps.device_status_metrics TO viewer;
GRANT SELECT ON TABLE openaps.device_status_metrics TO ext_openaps_app;
GRANT SELECT, INSERT ON TABLE openaps.device_status_metrics TO ingestor;


CREATE TABLE openaps.entries (
  seq_id BIGSERIAL PRIMARY KEY,
  user_id INTEGER,
  id VARCHAR,
  sgv NUMERIC,
  direction VARCHAR,
  device VARCHAR,
  type VARCHAR,
  rssi NUMERIC,
  rawbg NUMERIC,
  trend VARCHAR,
  glucose NUMERIC,
  mbg NUMERIC,
  delta NUMERIC,
  filtered NUMERIC,
  unfiltered NUMERIC,
  noise NUMERIC,  
  "scale" NUMERIC,
  slope NUMERIC,
  intercept NUMERIC,
  system_time VARCHAR,
  source_entity INTEGER,
  raw_json JSONB,
  "date" timestamp
);
GRANT SELECT ON TABLE openaps.entries TO viewer;
GRANT SELECT ON TABLE openaps.entries TO ext_openaps_app;
GRANT SELECT, INSERT ON TABLE openaps.entries TO ingestor;


CREATE TABLE openaps.profile (
  seq_id BIGSERIAL PRIMARY KEY,
  user_id INTEGER,
  "id" VARCHAR,
  "default_profile" text,
  mills int8,
  units VARCHAR,
  start_date TIMESTAMP,
  source_entity INTEGER,
  raw_json JSONB,
  created_at timestamp
);
GRANT SELECT ON TABLE openaps.profile TO viewer;
GRANT SELECT ON TABLE openaps.profile TO ext_openaps_app;
GRANT SELECT, INSERT ON TABLE openaps.profile TO ingestor;
GRANT SELECT ON openaps.profile TO ext_openaps_app;


CREATE TABLE openaps.treatments (
  seq_id BIGSERIAL PRIMARY KEY,
  user_id INTEGER,
  "id" VARCHAR,
  event_type VARCHAR,
  timestamp TIMESTAMP,
  insulin NUMERIC,
  carbs NUMERIC,
  protein NUMERIC,
  fat NUMERIC,
  glucose NUMERIC,
  glucose_type VARCHAR,
  food_type VARCHAR,
  temp VARCHAR,
  rate NUMERIC,
  duration NUMERIC,
  units VARCHAR,
  amount NUMERIC,
  absolute NUMERIC,
  medtronic VARCHAR,
  type VARCHAR,
  absorption_time NUMERIC,
  unabsorbed NUMERIC,
  ratio NUMERIC,
  target_top NUMERIC,
  target_bottom NUMERIC,
  fixed NUMERIC,
  programmed VARCHAR,
  reason VARCHAR,
  notes TEXT,
  entered_by VARCHAR,
  source_entity INTEGER,
  raw_json JSONB,
  created_at timestamp
);
GRANT SELECT ON TABLE openaps.treatments TO viewer;
GRANT SELECT ON TABLE openaps.treatments TO ext_openaps_app;
GRANT SELECT, INSERT ON TABLE openaps.treatments TO ingestor;


CREATE TABLE openaps.member_demographics (
  seq_id bigserial NOT NULL,
  ts timestamp NULL,
  project_member_id int4 NULL,
  date_of_birth date NULL,
  gender varchar NULL,
  ethnicity varchar NULL,
  country varchar NULL,
  first_diagnosed_date date NULL,
  first_insulin_pump_date date NULL,
  first_glucose_monitor_date date NULL,
  first_diy_closed_loop_date date NULL,
  diy_closed_loop_type varchar NULL,
  who_uses_the_closed_loop_system varchar NULL,
  weight varchar NULL,
  height varchar NULL,
  insulin_units_per_day numeric NULL,
  basal_insulin_units_per_day numeric NULL,
  carb_grams_per_day numeric NULL,
  last_lab_reported_a1c numeric NULL,
  last_lab_reported_a1c_date date NULL,
  inserted_ts timestamp NULL DEFAULT now(),
  updated_ts TIMESTAMP,
  CONSTRAINT member_demographics_project_member_id_pkey UNIQUE (project_member_id, ts)
);
GRANT SELECT ON TABLE openaps.member_demographics TO viewer;
GRANT SELECT ON TABLE openaps.member_demographics TO admin_viewer;


CREATE TABLE openaps.source_entities (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR,
  inserted_ts TIMESTAMP
	);
GRANT SELECT, INSERT ON TABLE openaps.source_entities TO ingestor;
GRANT SELECT ON TABLE openaps.source_entities TO viewer;
GRANT SELECT ON TABLE openaps.source_entities TO admin_viewer;

INSERT INTO openaps.source_entities
(id, name, inserted_ts)
values
(1, 'OpenAPS Data Commons', CURRENT_TIMESTAMP),
(2, 'NightScout Data Commons', CURRENT_TIMESTAMP);


-- this statement pre-creates the etl python scheduler table, so that ingestor does not need create tables perms
CREATE TABLE openaps.apscheduler_jobs (
  id VARCHAR(191) NOT NULL,
  next_run_time FLOAT(25),
  job_state BYTEA NOT NULL,
  PRIMARY KEY (id)
);
GRANT SELECT, INSERT, UPDATE ON TABLE openaps.apscheduler_jobs TO ingestor;


GRANT USAGE ON ALL SEQUENCES IN SCHEMA openaps TO ingestor;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA openaps TO viewer;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA openaps TO admin_viewer;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA openaps TO ext_openaps_app;

