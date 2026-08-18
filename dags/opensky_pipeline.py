from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.snowflake.operators.snowflake import SQLExecuteQueryOperator
from airflow.utils.email import send_email


def task_failure_alert(context):
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    execution_date = context["logical_date"]
    log_url = context["task_instance"].log_url

    send_email(
        to=["maazdanish321@gmail.com"],
        subject=f"🚨 Airflow Task Failed: {dag_id}.{task_id}",
        html_content=f"""
        <h2>🚨 OpenSky Pipeline Task Failed</h2>

        <p><strong>DAG:</strong> {dag_id}</p>
        <p><strong>Task:</strong> {task_id}</p>
        <p><strong>Execution Time:</strong> {execution_date}</p>

        <p>
            <strong>Logs:</strong>
            <a href="{log_url}">Open Airflow Task Logs</a>
        </p>

        <hr>

        <p>
            Please check the Airflow logs to identify the root cause.
        </p>
        """,
    )


with DAG(
    dag_id="opensky_pipeline",
    start_date=datetime(2026, 8, 11),
    schedule="@hourly",
    catchup=False,
    on_failure_callback=task_failure_alert,
) as dag:

    # =========================
    # EXTRACT
    # =========================

    extract_opensky = BashOperator(
        task_id="extract_opensky",
        bash_command="python /opt/airflow/scripts/extract_opensky.py",
    )

    # =========================
    # UPLOAD TO S3
    # =========================

    upload_to_s3 = BashOperator(
        task_id="upload_to_s3",
        bash_command="python /opt/airflow/scripts/upload_to_s3.py",
    )

    # =========================
    # BRONZE / RAW
    # =========================

    load_snowflake_raw = SQLExecuteQueryOperator(
        task_id="load_snowflake_raw",
        conn_id="snowflake_conn",
        sql="sql/bronze/load_bronze.sql",
    )

    # =========================
    # SILVER
    # =========================

    transform_silver = SQLExecuteQueryOperator(
        task_id="transform_silver",
        conn_id="snowflake_conn",
        sql="sql/silver/transform_silver.sql",
    )

    # =========================
    # GOLD
    # =========================

    flights_per_country_hour = SQLExecuteQueryOperator(
        task_id="flights_per_country_hour",
        conn_id="snowflake_conn",
        sql="sql/gold/flights_per_country_hour.sql",
    )

    aircraft_category_stats = SQLExecuteQueryOperator(
        task_id="aircraft_category_stats",
        conn_id="snowflake_conn",
        sql="sql/gold/aircraft_category_stats.sql",
    )

    busiest_airspace_regions = SQLExecuteQueryOperator(
        task_id="busiest_airspace_regions",
        conn_id="snowflake_conn",
        sql="sql/gold/busiest_airspace_regions.sql",
    )
    airspace_activity = SQLExecuteQueryOperator(
        task_id="airspace_activity",
        conn_id="snowflake_conn",
    	sql="sql/gold/airspace_activity.sql",
    )
    # =========================
    # DATA QUALITY
    # =========================

    check_raw = SQLExecuteQueryOperator(
        task_id="check_raw",
        conn_id="snowflake_conn",
        sql="sql/quality/check_raw.sql",
    )

    check_silver = SQLExecuteQueryOperator(
        task_id="check_silver",
        conn_id="snowflake_conn",
        sql="sql/quality/check_silver.sql",
    )

    check_gold = SQLExecuteQueryOperator(
        task_id="check_gold",
        conn_id="snowflake_conn",
        sql="sql/quality/check_gold.sql",
    )

    check_duplicates = SQLExecuteQueryOperator(
        task_id="check_duplicates",
        conn_id="snowflake_conn",
        sql="sql/quality/check_duplicates.sql",
    )

    check_coordinates = SQLExecuteQueryOperator(
        task_id="check_coordinates",
        conn_id="snowflake_conn",
        sql="sql/quality/check_coordinates.sql",
    )

    # =========================
    # PIPELINE DEPENDENCIES
    # =========================

    extract_opensky >> upload_to_s3 >> load_snowflake_raw >> transform_silver

    transform_silver >> [
        flights_per_country_hour,
        aircraft_category_stats,
	airspace_activity,
        busiest_airspace_regions,
    ]

    gold_tasks = [
   	 flights_per_country_hour,
   	 aircraft_category_stats,
 	 airspace_activity,
   	 busiest_airspace_regions,
    ]

    quality_checks = [
   	 check_raw,
   	 check_silver,
   	 check_gold,
   	 check_duplicates,
   	 check_coordinates,
    ]

    for gold_task in gold_tasks:
   	 for quality_check in quality_checks:
       		 gold_task >> quality_check
