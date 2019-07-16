-----------------------------------------

--Create View: Demographics clean step1

-----------------------------------------
-----------------------------------------

--Last Modified: 12/7/2019
--Written By: Matthew Taylor
--Cleaning demographics data
--Converting height and weight strings to integers and converting to uniform units (metric)
--Convert dob and diabetes diagnose dates to years since, and putting into brackets (eg 5-10 years)

--Parent tables/views:
--openaps.member_demographics (table)
-----------------------------------------
-----------------------------------------


create view openaps.demographics_clean_step1
as (
select
	t1.seq_id
	,height_feet
	,height_inches
	,round(case when height_cm is null then height_feet*30.48 + coalesce(height_inches,0) * 2.54 else height_cm end,0) as height_cm
	,weight_cleaned
	,weight_units
	,round(case when weight_units = 'kg' then weight_cleaned
		when weight_units = 'lbs' then weight_cleaned*0.453592
		else null end,0) as weight_kg
	,age_years
	,age_bracket
	,years_since_diagnosed
	,years_since_diagnosed_bracket
from
(
	select
		t1.*
		,cast(substring(case when height_units = 'feet/inch' then left(height,1)  else null end,'[0-9]{1,2}') as integer) as height_feet
		,cast(substring(trim(trim(case 
			when height like '%''%' then trim(left(split_part(height,'''',2),2),'"')
			when height like '%"%' then trim(left(split_part(height,'"',2),2),'"')
			when height like '%´%' then trim(left(split_part(height,'´',2),2),'"')
			else null end,'.'),''),'[0-9]{1,2}') as integer) as height_inches
		,cast(substring(case 
			when height_units <> 'feet/inch' and height like '%,%' then left(split_part(height,',',1) ||split_part(height,',',2),3) 
			when height_units <> 'feet/inch' and height like '%.%' then left(split_part(height,'.',1) ||split_part(height,'.',2),3)
			when height_units <> 'feet/inch' then left(trim(trim(height,'.'),','),3) else null end,'[0-9]{1,3}')as integer) as height_cm
		,case when weight like '%kg' then 'kg' else 'lbs' end weight_units
		,cast(substring(weight,'[0-9]{1,3}') as integer) as weight_cleaned
		,case when age_in_years > 150 then null else age_in_years end age_years
		,case
			when age_in_years between 0 and 5 then '0-5'
			when age_in_years between 6 and 10 then '06-10'
			when age_in_years between 11 and 15 then '11-15'
			when age_in_years between 16 and 20 then '16-20'
			when age_in_years between 21 and 30 then '21-30'
			when age_in_years between 31 and 45 then '31-45'
			when age_in_years between 46 and 60 then '46-60'
			when age_in_years > 60 then '60+'
			else null
		end as age_bracket
		,case
			when years_since_diagnosed between 0 and 2 then '0-2'
			when years_since_diagnosed between 3 and 5 then '03-5'
			when years_since_diagnosed between 6 and 10 then '06-10'
			when years_since_diagnosed between 11 and 20 then '11-20'
			when years_since_diagnosed > 20 then '20+'
		else null
		end as years_since_diagnosed_bracket
		
	from(
	 
	select
		seq_id
		,weight
		,height
		,case 
			when left(height,1) in ('3','4','5','6','7') then 'feet/inch'
			when height like '%cm%' then 'cm'
			when height like '%m%' then 'm'	
			else 'other'
		end as height_units	
		,date_of_birth
		,first_diagnosed_date
		,floor((current_date - date_of_birth)/365) as age_in_years
		,floor((current_date - first_diagnosed_date)/365) as years_since_diagnosed
	from openaps.openaps.member_demographics
	) t1
) t1
)
;

GRANT SELECT ON openaps.demographics_clean_step1 TO viewer;
GRANT SELECT ON openaps.demographics_clean_step1 TO admin_viewer;