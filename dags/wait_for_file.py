from airflow.sdk import task,dag
from currentpath import path_push
from airflow.models import Variable

file_path = path_push()

@dag
def file_check_dag():
    @task.sensor(poke_interval=60, timeout=600, mode="poke")
    def file_check_sensor():
        """Wait until file exists"""
        file_path = Variable.get("path")
        return file_path
