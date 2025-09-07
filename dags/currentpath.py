from dotenv import load_dotenv
import os
from pathlib import Path
from airflow.models import Variable
from airflow.sdk import task,dag


@dag
def path_push():
    @task
    def path():
        current_dir = Path(__file__).resolve().parent
        env_path = current_dir.parent / ".env"
        load_dotenv(dotenv_path=env_path)
        path =os.getenv(FILE_PATH)
        return Variable.set("path", path)
