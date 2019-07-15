
--DROP VIEW openaps.heroku_ids;
--DROP TABLE IF EXISTS openaps.device_status;
--DROP TABLE IF EXISTS openaps.device_status_metrics;
--DROP TABLE IF EXISTS openaps.entries;
--DROP TABLE IF EXISTS openaps."loop";
--DROP TABLE IF EXISTS openaps.profile;
--DROP TABLE IF EXISTS openaps.radio_adapter;
--DROP TABLE IF EXISTS openaps.treatments;
--DROP TABLE IF EXISTS openaps.heroku_apps;


CREATE TABLE openaps.device_status (
    seq_id BIGSERIAL PRIMARY KEY,
    app_id INTEGER,
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
	raw_json JSONB,
	created_at timestamp
);
ALTER TABLE openaps.device_status OWNER TO power_user;
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
    raw_json JSONB,
    enacted_timestamp TIMESTAMP
);
ALTER TABLE openaps.device_status_metrics OWNER TO power_user;
GRANT SELECT ON TABLE openaps.device_status_metrics TO viewer;
GRANT SELECT ON TABLE openaps.device_status_metrics TO ext_openaps_app;
GRANT SELECT, INSERT ON TABLE openaps.device_status_metrics TO ingestor;




CREATE TABLE openaps.entries (
	seq_id BIGSERIAL PRIMARY KEY,
	app_id INTEGER,
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
	raw_json JSONB,
	"date" timestamp
);
ALTER TABLE openaps.entries OWNER TO power_user;
GRANT SELECT ON TABLE openaps.entries TO viewer;
GRANT SELECT ON TABLE openaps.entries TO ext_openaps_app;
GRANT SELECT, INSERT ON TABLE openaps.entries TO ingestor;




CREATE TABLE openaps.profile (
	seq_id BIGSERIAL PRIMARY KEY,
	app_id INTEGER,
	"id" VARCHAR,
	"default_profile" text,
	mills int8,
	units VARCHAR,
	store JSON,
	loop_settings JSON,
	start_date TIMESTAMP,
	raw_json JSONB,
	created_at timestamp
);
ALTER TABLE openaps.profile OWNER TO power_user;
GRANT SELECT ON TABLE openaps.profile TO viewer;
GRANT SELECT ON TABLE openaps.profile TO ext_openaps_app;
GRANT SELECT, INSERT ON TABLE openaps.profile TO ingestor;
GRANT SELECT ON openaps.profile TO ext_openaps_app;






CREATE TABLE openaps.radio_adapter (
    seq_id BIGSERIAL PRIMARY KEY,
    app_id INTEGER,
	devicestatus_id text,
	last_tuned text,
	frequency NUMERIC,
	"name" text,
	firmware_version text,
	raw_json JSONB,
	hardware text
);
ALTER TABLE openaps.radio_adapter OWNER TO power_user;
GRANT SELECT ON TABLE openaps.radio_adapter TO viewer;
GRANT SELECT ON TABLE openaps.radio_adapter TO ext_openaps_app;
GRANT SELECT, INSERT ON TABLE openaps.radio_adapter TO ingestor;





CREATE TABLE openaps.treatments (
    seq_id BIGSERIAL PRIMARY KEY,
    app_id INTEGER,
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
	bolus JSON,
	boluscalc JSON,
	medtronic VARCHAR,
	type VARCHAR,
	absorption_time NUMERIC,
	unabsorbed NUMERIC,
	ratio NUMERIC,
	wizard JSON,
	target_top NUMERIC,
	target_bottom NUMERIC,
	fixed NUMERIC,
	programmed VARCHAR,
	reason VARCHAR,
	notes TEXT,
	entered_by VARCHAR,
	raw_json JSONB,
	created_at timestamp
);
ALTER TABLE openaps.treatments OWNER TO power_user;
GRANT SELECT ON TABLE openaps.treatments TO viewer;
GRANT SELECT ON TABLE openaps.treatments TO ext_openaps_app;
GRANT SELECT, INSERT ON TABLE openaps.treatments TO ingestor;




CREATE TABLE openaps.heroku_apps (

	id BIGSERIAL PRIMARY KEY,
	url VARCHAR,
	permission_withdrawn BOOL,
	withdrawal_date TIMESTAMP,
	created_ts TIMESTAMP

);
ALTER TABLE openaps.heroku_apps OWNER TO power_user;
GRANT SELECT, INSERT ON TABLE openaps.heroku_apps TO ingestor;




CREATE VIEW openaps.heroku_ids
AS SELECT id, created_ts FROM openaps.heroku_apps;

ALTER VIEW openaps.heroku_ids OWNER TO power_user;
GRANT SELECT ON openaps.heroku_ids TO viewer;
GRANT SELECT ON openaps.heroku_ids TO admin_viewer;


GRANT USAGE ON ALL SEQUENCES IN SCHEMA openaps TO ingestor;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA openaps TO viewer;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA openaps TO admin_viewer;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA openaps TO ext_openaps_app;