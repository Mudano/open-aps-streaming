--create a treatments view. This only adds an extra column do deal with some metabase oddities when sorting data

--Parent tables/views:
--openaps.treatments (table)
-----------------------------------------
-----------------------------------------

create view openaps.treatments_view
as
select 
	*
	,1 as count_column
from openaps.treatments
;

