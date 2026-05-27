from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/opt/airflow/ingestion')

default_args = {
    'owner': 'suttinan',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_ingestion():
    from fetch_weather import fetch_weather, transform_weather, load_to_postgres
    data = fetch_weather()
    df = transform_weather(data)
    load_to_postgres(df)
    print(f"✅ Ingested {len(df)} rows")

with DAG(
    dag_id='weather_pipeline',
    default_args=default_args,
    description='Daily weather data pipeline',
    schedule_interval='0 6 * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['weather', 'daily'],
) as dag:

    task_ingest = PythonOperator(
        task_id='ingest_weather',
        python_callable=run_ingestion,
    )

    task_dbt = BashOperator(
        task_id='dbt_transform',
        bash_command='cd /opt/airflow/dbt_project && dbt run --profiles-dir /opt/airflow/dbt_project',
    )

    task_ingest >> task_dbt