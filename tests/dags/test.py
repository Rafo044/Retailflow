from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def push_xcom(ti):
    data = {"message": "Hello MinIO XCom!"}
    ti.xcom_push(key="test_key", value=data)

def pull_xcom(ti):
    xcom_value = ti.xcom_pull(key="test_key", task_ids="push_task")
    print("Pulled XCom value:", xcom_value)

with DAG(
    dag_id="xcom_minio_test",
    start_date=datetime(2025, 9, 9),
    schedule=None,
    catchup=False,
) as dag:

    push_task = PythonOperator(
        task_id="push_task",
        python_callable=push_xcom,
    )

    pull_task = PythonOperator(
        task_id="pull_task",
        python_callable=pull_xcom,
    )

    push_task >> pull_task
