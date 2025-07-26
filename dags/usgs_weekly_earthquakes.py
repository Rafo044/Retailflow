from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
from sqlalchemy import create_engine, inspect

# DAG ayarları
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "astro_5e5026-postgres-1"
DB_PORT = "5432"
DB_NAME = "bank"
TABLE_NAME = "earthquakes_weekly"

def fetch_and_store_earthquakes():
    # 1. Tarix aralığı (son 7 gün)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)

    # 2. API çağırışı
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": start_date.isoformat(),
        "endtime": end_date.isoformat(),
        "orderby": "time"
    }

    response = requests.get(url, params=params)
    data = response.json()

    # 3. JSON → DataFrame
    features = data.get("features", [])
    records = []
    for quake in features:
        props = quake["properties"]
        records.append({
            "Yer": props.get("place"),
            "Magnituda": props.get("mag"),
            "Zaman_UTC": datetime.utcfromtimestamp(props["time"] / 1000),
            "Link": props.get("url")
        })

    df = pd.DataFrame(records)

    if df.empty:
        print("Bu həftə üçün zəlzələ tapılmadı.")
        return

    # 4. PostgreSQL bağlantısı qur
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # 5. Cədvəl yoxdursa yarat, varsa əlavə et
    inspector = inspect(engine)
    if not inspector.has_table(TABLE_NAME):
        df.to_sql(TABLE_NAME, engine, index=False, if_exists="replace")
        print(f"{TABLE_NAME} yaradıldı və {len(df)} sətir yazıldı.")
    else:
        df.to_sql(TABLE_NAME, engine, index=False, if_exists="append", method="multi")
        print(f"{TABLE_NAME} cədvəlinə {len(df)} yeni sətir əlavə edildi.")

# DAG tanımı
with DAG(
    dag_id="usgs_weekly_earthquakes_to_postgres",
    default_args=default_args,
    description="USGS zəlzələlərini hər həftə alıb PostgreSQL-ə yaz",
    schedule="@weekly",
    start_date=datetime(2025, 7, 1),
    catchup=False,
    tags=["earthquake", "usgs", "postgres"]
) as dag:

    task = PythonOperator(
        task_id="fetch_and_store_weekly_earthquakes",
        python_callable=fetch_and_store_earthquakes
    )

    task

