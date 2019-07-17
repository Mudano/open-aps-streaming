--Create a view to make corrections to country entries

--Parent tables/views:
--openaps.member_demographics (table)
-----------------------------------------
-----------------------------------------

create view openaps.country_ref
as(
select 
	replace(lower(country),'the ','') as country_original
	,case
		when replace(lower(country),'the ','') = 'uk' then 'united kingdom'
		when replace(lower(country),'the ','') = 'us' then 'united states of america'
		when replace(lower(country),'the ','') like 'u.s.a%' then 'united states of america'
		when replace(lower(country),'the ','') = 'usa' then 'united states of america'
		when replace(lower(country),'the ','') = 'united states' then 'united states of america'
		when replace(lower(country),'the ','') = 'españa' then 'spain'
		when replace(lower(country),'the ','') = 'italia' then 'italy'
		when replace(lower(country),'the ','') = '' then 'not available'
		else replace(lower(country),'the ','')
	end as country_corrected

from openaps.member_demographics

group by 1,2
)
;

