MERGE INTO OPENSKY_DB.SILVER.OPENSKY_CLEAN AS target

USING (

    SELECT
        ICAO24,

        NULLIF(
            UPPER(TRIM(CALLSIGN)),
            ''
        ) AS CALLSIGN,

        NULLIF(
            UPPER(TRIM(ORIGIN_COUNTRY)),
            ''
        ) AS ORIGIN_COUNTRY,

        LONGITUDE,
        LATITUDE,
        BARO_ALTITUDE,
        VELOCITY,
        TRUE_TRACK,
        VERTICAL_RATE,

        NULLIF(
            TRIM(SQUAWK),
            ''
        ) AS SQUAWK,

        ON_GROUND,
        NULLIF(TRIM(REGISTRATION), '') AS REGISTRATION,
        NULLIF(TRIM(MODEL), '') AS MODEL,
        NULLIF(TRIM(TYPECODE), '') AS TYPECODE,
        NULLIF(TRIM(SOURCE), '') AS SOURCE,

        LAST_SEEN,
        LAST_CONTACT,
        CATEGORY,
        TRANSPORT_KIND,
        INGESTION_TIMESTAMP

    FROM OPENSKY_DB.RAW.OPENSKY_RAW

    WHERE ICAO24 IS NOT NULL
      AND LAST_CONTACT IS NOT NULL
      AND LONGITUDE BETWEEN -180 AND 180
      AND LATITUDE BETWEEN -90 AND 90

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY ICAO24, LAST_CONTACT
        ORDER BY INGESTION_TIMESTAMP DESC
    ) = 1

) AS source

ON target.ICAO24 = source.ICAO24
AND target.LAST_CONTACT = source.LAST_CONTACT

WHEN NOT MATCHED THEN

    INSERT (
        ICAO24,
        CALLSIGN,
        ORIGIN_COUNTRY,
        LONGITUDE,
        LATITUDE,
        BARO_ALTITUDE,
        VELOCITY,
        TRUE_TRACK,
        VERTICAL_RATE,
        SQUAWK,
        ON_GROUND,
        REGISTRATION,
        MODEL,
        TYPECODE,
        SOURCE,
        LAST_SEEN,
        LAST_CONTACT,
        CATEGORY,
        TRANSPORT_KIND,
        INGESTION_TIMESTAMP
    )

    VALUES (
        source.ICAO24,
        source.CALLSIGN,
        source.ORIGIN_COUNTRY,
        source.LONGITUDE,
        source.LATITUDE,
        source.BARO_ALTITUDE,
        source.VELOCITY,
        source.TRUE_TRACK,
        source.VERTICAL_RATE,
        source.SQUAWK,
        source.ON_GROUND,
        source.REGISTRATION,
        source.MODEL,
        source.TYPECODE,
        source.SOURCE,
        source.LAST_SEEN,
        source.LAST_CONTACT,
        source.CATEGORY,
        source.TRANSPORT_KIND,
        source.INGESTION_TIMESTAMP
    );
