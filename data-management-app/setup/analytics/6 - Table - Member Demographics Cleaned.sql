-----------------------------------------

--Create Table: Member Demographics Cleaned

-----------------------------------------
-----------------------------------------

--Last Modified: 11/7/2019
--Written By: Matthew Taylor
--Join the derived country reference view and the cleaned demographics view to the member demographics table
--This will be our overall all cleaned dataset. Users can compare the original values to the cleaned values

--Parent tables/views:
--openaps.member_demographics (table)
--openaps.country_ref (view)
--openaps.demographics_clean_step1 (view)

-----------------------------------------
-----------------------------------------


create table openaps.member_demographics_cleaned
as (
select
	t1.seq_id
	,t1."timestamp"
	,t1.project_member_id
	,t1.date_of_birth
	,case when t1.gender = '' then 'Not Available' else t1.gender end as gender
	,t1.ethnicity
	,t1.country
	,t1.first_diagnosed_date
	,t1.first_insulin_pump_date
	,t1.first_glucose_monitor_date
	,t1.first_diy_closed_loop_date
	,t1.diy_closed_loop_type
	,t1.who_uses_the_closed_loop_system
	,t1.weight
	,t1.height
	,t1.insulin_units_per_day
	,t1.basal_insulin_units_per_day
	,t1.carb_grams_per_day
	,t1.last_lab_reported_a1c
	,t1.last_lab_reported_a1c_date
	,t1.inserted_ts
	,t3.height_feet as cleaned_height_ft
	,t3.height_inches as  cleaned_height_in
	,t3.height_cm as cleaned_height_cm
	,t3.weight_cleaned as cleaned_weight
	,t3.weight_units as cleaned_weight_units
	,t3.weight_kg as cleaned_weight_kg
	,t3.age_years
	,t3.age_bracket
	,t3.years_since_diagnosed
	,t3.years_since_diagnosed_bracket
	,t2.country_corrected
from openaps.openaps.member_demographics t1

left join openaps.country_ref t2
	on replace(lower(t1.country),'the ','') = t2.country_original

left join openaps.demographics_clean_step1 t3
	on t1.seq_id = t3.seq_id
)
;

--Add indexing on fields that are used as group bys and filters within the visualisation to improve performance
create unique index seq_id_indx on openaps.member_demographics_cleaned (seq_id);
create index project_member_id_indx on openaps.member_demographics_cleaned (project_member_id);


GRANT SELECT ON openaps.member_demographics_cleaned TO viewer;
GRANT SELECT ON openaps.member_demographics_cleaned TO admin_viewer;