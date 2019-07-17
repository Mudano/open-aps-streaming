--Determine whether open or closed loop user
--logic for if a user is closed loop for a given day.
--if we join to our entries table we can use as a referece. if no join is made then we assume open loop

--Parent tables/views:
--openaps.device_status (table)
-----------------------------------------
-----------------------------------------

create view openaps.loop_typ_reference
as
select 
	app_id
	,"created_at"::date as device_date
	,case when max(loop_iob) is null then 'open loop' else 'closed loop' end as Loop_type
from openaps.device_status

group by 1,2
;

