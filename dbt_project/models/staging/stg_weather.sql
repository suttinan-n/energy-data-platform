with source as (
    select *
    from {{ source('raw', 'raw_weather') }}
),
cleaned as (
    select id,
        date::date as weather_date,
        temp_max::numeric(5, 2) as temp_max_celsius,
        temp_min::numeric(5, 2) as temp_min_celsius,
        round(
            cast((temp_max + temp_min) / 2 as numeric),
            2
        ) as temp_avg_celsius,
        precipitation::numeric(8, 2) as precipitation_mm,
        windspeed_max::numeric(8, 2) as windspeed_max_kmh,
        location,
        created_at
    from source
    where temp_max is not null
        and temp_min is not null
)
select *
from cleaned