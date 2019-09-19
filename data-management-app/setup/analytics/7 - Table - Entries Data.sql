-----------------------------------------

--Create Table: Entries Data

-----------------------------------------
-----------------------------------------

--Last Modified: 11/7/2019
--Written By: Matthew Taylor
--Notes: 
--Used to build the majority of vizes on the Blood Glucose Entries Dashboard. 
--Makes modifications to fields from the openaps.entries dataset and joins with cleaned demographics data

--Parent tables/views:
--openaps.entries (table)
--openaps.time_reference (table)
--openaps.loop_type_reference (view)
--openaps.member_demographics_cleaned (table)

-----------------------------------------
-----------------------------------------

create table openaps.entries_data
as (
select
    t1.app_id
    ,t1.entry_datetime
    ,to_timestamp('1900-01-01 ' || t2.start_tm,'YYYY-MM-DD HH24:MI:SS') start_tmstamp
    ,to_timestamp('1900-01-01 ' || t2.end_tm,'YYYY-MM-DD HH24:MI:SS') as end_tmstamp
    ,t1.date_exact
    ,t1.event_type
    ,t1.noise
    ,t1.rssi
    ,t1.rawbg
    ,t1.trend
    ,t1.glucose
    ,t1.mbg
    ,t1.delta
    ,t1.filtered
    ,t1.unfiltered
    ,t1.direction
    ,t1.scale
    ,t1.slope
    ,t1.intercept
    ,t1.sgv_unaltered
    ,t1.sgv_mmol_L
    ,t1.source_entity
    ,case when t3.loop_type is null then 'open loop' else t3.loop_type end as loop_type
    ,t1.device
    ,case
        when lower(t1.device) like '%xdrip%' then 'xDrip'
        when lower(t1.device) like '%libre/0%' then 'Libre'
        when lower(t1.device) like '%miaomiao%' then 'MiaoMiao'
        when lower(t1.device) like '%share2' then 'Dexcom'
        when lower(t1.device) like '%medtronic%' then 'Medtronic'
        else t1.device
    end as device_group
    ,t4.date_of_birth
    ,t4.gender
    ,t4.ethnicity
    ,t4.country
    ,t4.first_diagnosed_date
    ,t4.first_insulin_pump_date
    ,t4.first_glucose_monitor_date
    ,t4.first_diy_closed_loop_date
    ,t4.diy_closed_loop_type
    ,t4.who_uses_the_closed_loop_system
    ,t4.weight
    ,t4.height
    ,t4.insulin_units_per_day
    ,t4.basal_insulin_units_per_day
    ,t4.carb_grams_per_day
    ,t4.last_lab_reported_a1c
    ,t4.last_lab_reported_a1c_date
    ,t4.inserted_ts
    ,t4.cleaned_height_ft
    ,t4.cleaned_height_in
    ,t4.cleaned_height_cm
    ,t4.cleaned_weight
    ,t4.cleaned_weight_units
    ,t4.cleaned_weight_kg
    ,t4.age_years
    ,t4.age_bracket
    ,t4.years_since_diagnosed
    ,t4.years_since_diagnosed_bracket
    ,t4.country_corrected
from (
select
    user_id as app_id
    ,"id" as entry_id
    ,"date" as entry_datetime
    ,"date"::time as time_exact
    ,"date"::date as date_exact
    ,"type" || ' - entry' as event_type
    ,device
    ,noise
    ,rssi
    ,rawbg
    ,trend
    ,glucose
    ,mbg
    ,delta
    ,filtered
    ,unfiltered
    ,direction
    ,scale
    ,slope
    ,intercept
    ,sgv as sgv_unaltered
    ,case
        when sgv < 25
            then sgv
        else sgv / 18
     end as sgv_mmol_L
    ,source_entity

from openaps.entries
)t1
left join openaps.time_reference t2
    on t1.time_exact >= t2.start_tm
    and t1.time_exact < t2.end_tm
left join openaps.loop_typ_reference t3
    on t1.app_id = t3.user_id
    and t1.date_exact = t3.device_date
left join openaps.member_demographics_cleaned t4
    on t1.app_id = t4.project_member_id
)
;

--Add indexing on fields that are used as group bys and filters within the visualisation to improve performance

create index app_id_indx on openaps.entries_data (app_id);
create index entry_datetime_indx on openaps.entries_data (entry_datetime);
create index age_indx on openaps.entries_data (age_bracket);
create index diagnosed_indx on openaps.entries_data (years_since_diagnosed_bracket);
create index date_exact_indx on openaps.entries_data (date_exact);
create index device_group_indx on openaps.entries_data (device_group);
create index country_indx on openaps.entries_data (country_corrected);


GRANT SELECT ON openaps.entries_data TO viewer;
GRANT SELECT ON openaps.entries_data TO admin_viewer;
