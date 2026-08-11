from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from scripts.test_opensky_api import main


with DAG(
    dag_id="opensky_pipeline",
    start_date=datetime(2026, 8, 11),
    schedule="@hourly",
    catchup=False,
) as dag:

    extract_opensky = PythonOperator(
        task_id="extract_opensky",
        python_callable=main,
    )