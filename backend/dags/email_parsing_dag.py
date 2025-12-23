import sys
sys.path.append('/opt/airflow/backend')
from airflow import DAG
from airflow.operators.python import PythonOperator
from sensors.custom_inbox_sensor import CustomInboxSensor
from scripts.email_parsing import parse_latest_requirement_email
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'email_parsing_dag',
    default_args=default_args,
    description='DAG to monitor inbox and parse latest "Requirement" email',
    schedule_interval='* * * * *',  # Run every minute
    start_date=datetime(2025, 10, 1),
    catchup=False,
    max_active_runs=1,
    tags=['email', 'enquiry'],
) as dag:
    check_email = CustomInboxSensor(
        task_id='check_for_new_email',
        poke_interval=60,
        timeout=3600,
        soft_fail=False,
    )
    parse_email = PythonOperator(
        task_id='parse_latest_requirement_email',
        python_callable=parse_latest_requirement_email,
        provide_context=True,
    )
    check_email >> parse_email