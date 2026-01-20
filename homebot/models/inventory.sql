WITH leases AS (
    SELECT 
        "mac-address" AS mac_address,
        address AS ip_address,
        "host-name" AS hostname,
        status,
        "last-seen" AS last_seen
    FROM {{ source('network', 'raw_leases') }}
),

metadata AS (
    SELECT * FROM {{ ref('device_metadata') }}
)

SELECT
    l.mac_address,
    l.ip_address,
    l.hostname,
    l.status,
    l.last_seen,
    COALESCE(m.device_type, 'Unknown') AS device_type,
    m.owner,
    m.location
FROM leases l
LEFT JOIN metadata m ON l.mac_address = m.mac_address
