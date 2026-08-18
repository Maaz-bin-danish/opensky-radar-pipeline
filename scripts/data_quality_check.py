from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook


def check():

    hook = SnowflakeHook(
        snowflake_conn_id="snowflake_conn"
    )

    checks = []

    # RAW row count
    raw_rows = hook.get_first("""
        SELECT COUNT(*)
        FROM OPENSKY_DB.RAW.OPENSKY_RAW
    """)[0]

    print(f"RAW rows: {raw_rows}")

    checks.append(
        ("RAW row count", raw_rows > 0)
    )

    # SILVER row count
    silver_rows = hook.get_first("""
        SELECT COUNT(*)
        FROM OPENSKY_DB.SILVER.OPENSKY_CLEAN
    """)[0]

    print(f"SILVER rows: {silver_rows}")

    checks.append(
        ("SILVER row count", silver_rows > 0)
    )

    # GOLD tables
    gold_tables = [
        "FLIGHTS_PER_COUNTRY_HOUR",
        "AIRCRAFT_CATEGORY_STATS",
        "BUSIEST_AIRSPACE_REGIONS",
    ]

    for table in gold_tables:

        count = hook.get_first(
            f"""
            SELECT COUNT(*)
            FROM OPENSKY_DB.GOLD.{table}
            """
        )[0]

        print(f"{table}: {count}")

        checks.append(
            (f"GOLD {table}", count > 0)
        )

    # Coordinate validation
    invalid_coordinates = hook.get_first("""
        SELECT COUNT(*)
        FROM OPENSKY_DB.SILVER.OPENSKY_CLEAN
        WHERE LATITUDE NOT BETWEEN -90 AND 90
           OR LONGITUDE NOT BETWEEN -180 AND 180
    """)[0]

    print(f"Invalid coordinates: {invalid_coordinates}")

    checks.append(
        ("Coordinate validation", invalid_coordinates == 0)
    )

    # Duplicate validation
    duplicate_groups = hook.get_first("""
        SELECT COUNT(*)
        FROM (
            SELECT ICAO24, LAST_CONTACT
            FROM OPENSKY_DB.SILVER.OPENSKY_CLEAN
            GROUP BY ICAO24, LAST_CONTACT
            HAVING COUNT(*) > 1
        )
    """)[0]

    print(f"Duplicate groups: {duplicate_groups}")

    checks.append(
        ("Duplicate validation", duplicate_groups == 0)
    )

    print("\nDATA QUALITY RESULTS")

    failed = False

    for name, passed in checks:

        if passed:
            print(f"PASS: {name}")
        else:
            print(f"FAIL: {name}")
            failed = True

    if failed:
        raise RuntimeError(
            "DATA QUALITY CHECK FAILED"
        )

    print("\nALL DATA QUALITY CHECKS PASSED")


if __name__ == "__main__":
    check()
