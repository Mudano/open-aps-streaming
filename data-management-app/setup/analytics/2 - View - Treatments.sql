
-----------------------------------------

--Create View: Treatments
-----------------------------------------
-----------------------------------------

--Last Modified: 12/7/2019
--Written By: Matthew Taylor
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

GRANT SELECT ON openaps.treatments_view TO viewer;
GRANT SELECT ON openaps.treatments_view TO admin_viewer;