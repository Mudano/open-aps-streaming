

def does_table_exist(table_name, pg_connection):
    table_check_sql_string = \
        "select exists(select * from information_schema.tables where table_name=%s and table_schema='openaps')"

    try:
        with pg_connection.cursor() as cursor:
            cursor.execute(table_check_sql_string, (table_name,))
            data = cursor.fetchone()[0]
            return data
    except Exception as e:
        print(f"Error encountered checking if {table_name} exists, table removal will be attempted: {e}")
        return True


def do_tables_exist(table_names, pg_connection):

    # initialised True, will be set to false if any table checks fail to find the tables
    all_tables_exist = True

    try:
        for name in table_names:
            table_exists = does_table_exist(name, pg_connection)
            all_tables_exist = all_tables_exist and table_exists
        return all_tables_exist
    except Exception as e:
        print(f"Database connection failed checking table existence, table removal will be attempted: {e}")
        return True


def remove_table(table_name, pg_connection):
    # can't parameterise a drop statement, don't expose this function to arbitrary input as it could be used for
    # sql injection
    table_remove_sql_string = f"drop table \"{table_name}\""

    try:
        with pg_connection.cursor() as cursor:
            cursor.execute(table_remove_sql_string, (table_name,))
            return True
    except Exception as e:
        print(f"Error dropping {table_name}, ETL will not progress: {e}")
        return False


def remove_tables(table_names, pg_connection):

    # initialised True, will be set to false if any table deletions fail
    all_tables_dropped = True

    try:
        for name in table_names:
            table_dropped = remove_table(name, pg_connection)
            all_tables_dropped = all_tables_dropped and table_dropped
        return all_tables_dropped
    except Exception as e:
        print(f"Error encountered trying to delete a view table, ETL will not progress: {e}")
        return False


def create_tables(pg_connection):
    create_demographics_table(pg_connection)
    create_entries_table(pg_connection)


def create_demographics_table(pg_connection):
    demo_table_sql_string = """
    create table openaps.member_demographics_cleaned
    as (
      select
        t1.seq_id, t1.ts, t1.project_member_id, t1.date_of_birth,
        case when t1.gender = '' then 'Not Available' else t1.gender end as gender, 
        t1.ethnicity, t1.country, t1.first_diagnosed_date, t1.first_insulin_pump_date,
        t1.first_glucose_monitor_date, t1.first_diy_closed_loop_date, t1.diy_closed_loop_type,
        t1.who_uses_the_closed_loop_system, t1.weight, t1.height, t1.insulin_units_per_day,
        t1.basal_insulin_units_per_day, t1.carb_grams_per_day, t1.last_lab_reported_a1c,
        t1.last_lab_reported_a1c_date, t1.inserted_ts, t3.height_feet as cleaned_height_ft,
        t3.height_inches as  cleaned_height_in, t3.height_cm as cleaned_height_cm,
        t3.weight_cleaned as cleaned_weight, t3.weight_units as cleaned_weight_units,
        t3.weight_kg as cleaned_weight_kg, t3.age_years, t3.age_bracket, t3.years_since_diagnosed,
        t3.years_since_diagnosed_bracket, t2.country_corrected
      from openaps.member_demographics t1
      left join openaps.country_ref t2
        on replace(lower(t1.country),'the ','') = t2.country_original
      left join openaps.demographics_clean_step1 t3
        on t1.seq_id = t3.seq_id
    );

    create unique index seq_id_indx on openaps.member_demographics_cleaned (seq_id);
    create index project_member_id_indx on openaps.member_demographics_cleaned (project_member_id);
    
    GRANT SELECT ON openaps.member_demographics_cleaned TO viewer; 
    """

    try:
        with pg_connection.cursor() as cursor:
            cursor.execute(demo_table_sql_string)
            return True
    except Exception as e:
        print(f"Error encountered creating `member_demographics_cleaned` table: {e}")
        return False


def create_entries_table(pg_connection):
    entries_table_sql_string = """
    create table openaps.entries_data
    as (
      select t1.app_id, t1.entry_datetime,
      to_timestamp('1900-01-01 ' || t2.start_tm,'YYYY-MM-DD HH24:MI:SS') start_tmstamp,
      to_timestamp('1900-01-01 ' || t2.end_tm,'YYYY-MM-DD HH24:MI:SS') as end_tmstamp,
      t1.date_exact, t1.event_type, t1.noise, t1.rssi, t1.rawbg, t1.trend, t1.glucose,
      t1.mbg, t1.delta, t1.filtered, t1.unfiltered, t1.direction, t1.scale, t1.slope,
      t1.intercept, t1.sgv_unaltered, t1.sgv_mmol_L,
      case when t3.loop_type is null then 'open loop' else t3.loop_type end as loop_type,
      t1.device,
      case
        when lower(t1.device) like '%xdrip%' then 'xDrip'
        when lower(t1.device) like '%libre/0%' then 'Libre'
        when lower(t1.device) like '%miaomiao%' then 'MiaoMiao'
        when lower(t1.device) like '%share2' then 'Dexcom'
        when lower(t1.device) like '%medtronic%' then 'Medtronic'
        else t1.device
      end as device_group, t4.date_of_birth, t4.gender, t4.ethnicity, t4.country,
      t4.first_diagnosed_date, t4.first_insulin_pump_date, t4.first_glucose_monitor_date,
      t4.first_diy_closed_loop_date, t4.diy_closed_loop_type, t4.who_uses_the_closed_loop_system,
      t4.weight, t4.height, t4.insulin_units_per_day, t4.basal_insulin_units_per_day, t4.carb_grams_per_day,
      t4.last_lab_reported_a1c, t4.last_lab_reported_a1c_date, t4.inserted_ts, t4.cleaned_height_ft,
      t4.cleaned_height_in, t4.cleaned_height_cm, t4.cleaned_weight, t4.cleaned_weight_units, t4.cleaned_weight_kg,
      t4.age_years, t4.age_bracket, t4.years_since_diagnosed, t4.years_since_diagnosed_bracket, t4.country_corrected
      from (
        select
          user_id as "app_id", "id" as entry_id, "date" as entry_datetime, "date"::time as time_exact, "date"::date as date_exact,
          "type" || ' - entry' as event_type , device, noise, rssi, rawbg, trend, glucose, mbg, delta, filtered,
          unfiltered, direction, scale, slope, intercept, sgv as sgv_unaltered,
          case 
            when sgv < 25 then sgv else sgv / 18
          end as sgv_mmol_L
        from openaps.entries
      ) t1
    left join openaps.time_reference t2 on t1.time_exact >= t2.start_tm and t1.time_exact < t2.end_tm
    left join openaps.loop_typ_reference t3 on t1.app_id = t3.user_id and t1.date_exact = t3.device_date
    left join openaps.member_demographics_cleaned t4 on t1.app_id = t4.seq_id
    );

    create index app_id_indx on openaps.entries_data (app_id);
    create index entry_datetime_indx on openaps.entries_data (entry_datetime);
    create index age_indx on openaps.entries_data (age_bracket);
    create index diagnosed_indx on openaps.entries_data (years_since_diagnosed_bracket);
    create index date_exact_indx on openaps.entries_data (date_exact);
    create index device_group_indx on openaps.entries_data (device_group);
    create index country_indx on openaps.entries_data (country_corrected);
    
    GRANT SELECT ON openaps.entries_data TO viewer; 
    """

    try:
        with pg_connection.cursor() as cursor:
            cursor.execute(entries_table_sql_string)
            return True
    except Exception as e:
        print(f"Error encountered creating `entries_data` table: {e}")
        return False
