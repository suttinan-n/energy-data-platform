with stg as (
    select *
    from {{ ref('stg_weather') }}
),
daily_summary as (
    select weather_date,
        location,
        temp_max_celsius,
        temp_min_celsius,
        temp_avg_celsius,
        precipitation_mm,
        windspeed_max_kmh,
        -- categorize temperature
        case
            when temp_avg_celsius >= 35 then 'Very Hot'
            when temp_avg_celsius >= 30 then 'Hot'
            when temp_avg_celsius >= 25 then 'Warm'
            else 'Cool'
        end as temp_category,
        -- categorize rain
        case
            when precipitation_mm = 0 then 'No Rain'
            when precipitation_mm < 5 then 'Light Rain'
            when precipitation_mm < 20 then 'Moderate Rain'
            else 'Heavy Rain'
        end as rain_category
    from stg
)
select *
from daily_summary