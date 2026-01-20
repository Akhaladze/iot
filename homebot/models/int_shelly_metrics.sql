SELECT 
    hostname,
    scanned_at,
    gen,
    -- Power in Watts
    CASE 
        WHEN gen = 1 THEN (raw_status::JSON)->'meters'->0->>'power'
        WHEN gen = 2 THEN (raw_status::JSON)->'switch:0'->>'apower'
    END AS power_w,
    -- Voltage in Volts
    CASE 
        WHEN gen = 1 THEN (raw_status::JSON)->'meters'->0->>'voltage'
        WHEN gen = 2 THEN (raw_status::JSON)->'switch:0'->>'voltage'
    END AS voltage_v,
    -- Uptime in seconds
    CASE 
        WHEN gen = 1 THEN raw_status::JSON->>'uptime'
        WHEN gen = 2 THEN (raw_status::JSON)->'sys'->>'uptime'
    END AS uptime_s,
    -- Internal temperature in Celsius
    CASE 
        WHEN gen = 1 THEN (raw_status::JSON)->'tmp'->>'tC'
        WHEN gen = 2 THEN (raw_status::JSON)->'switch:0'->'temperature'->>'tC'
    END AS temp_c
FROM {{ source('network', 'raw_shelly_data') }}
