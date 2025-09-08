import re
from pandas import DataFrame
from airflow.sdk import task, dag, Asset
import pandas as pd
from datetime import datetime
from io import StringIO
from airflow.providers.mysql.hooks.mysql import MySqlHook
import requests

url = "https://raw.githubusercontent.com/Rafo044/Retailflow/refs/heads/main/data/retaildata.csv"

# ========   Extract Transform  Load  ===========

@dag(
    schedule="@daily",
    start_date=datetime(2025, 9, 1),  # keçmiş tarix
    catchup=False,
    tags=["retail", "etl"]
)
def etl():

    @task()
    def extract() -> DataFrame:
        response = requests.get(url)
        print(response.status_code)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
        else:
            raise Exception("Failed to fetch data")
        return df

    #Transform
    @task()
    def handling(df: DataFrame) -> DataFrame:
        df = df.drop_duplicates(subset=['invoice_no'])
        df = df.fillna({'payment_method': 'Unknown', 'category': 'Misc'})
        return df

    @task()
    def total_revinue(df: DataFrame) -> DataFrame:
        df["total_revinue"] = pd.to_numeric(df["quantity"], errors="coerce") * pd.to_numeric(df["price"], errors="coerce")
        # average_order_value row-level üçün sadələşdirilmiş
        df["average_order_value"] = df["total_revinue"] / 1.0
        df["total_quantity_solid"] = df["quantity"].sum()
        return df

    @task()
    def month_weekday(df: DataFrame) -> DataFrame:
        df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
        df["month"] = df["invoice_date"].dt.month
        df["weekday"] = df["invoice_date"].dt.day_name()
        return df

    @task()
    def normalization(df: DataFrame) -> DataFrame:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
        df["total_revinue"] = pd.to_numeric(df["total_revinue"], errors="coerce").fillna(0.0)
        df["average_order_value"] = pd.to_numeric(df["average_order_value"], errors="coerce").fillna(0.0)
        df["total_quantity_solid"] = pd.to_numeric(df["total_quantity_solid"], errors="coerce").fillna(0).astype(int)
        df['category'] = df['category'].astype(str).str.strip().str.title()
        return df

    #Load
    @task()
    def load(df: DataFrame):
        hook = MySqlHook(mysql_conn_id='retailflow')
        target_fields = list(df.columns)
        rows = [tuple(x) for x in df[target_fields].to_numpy()]
        hook.insert_rows(table='transformed_data', rows=rows, target_fields=target_fields)

    # Task chain
    df_extracted = extract()
    df_handled = handling(df_extracted)
    df_total = total_revinue(df_handled)
    df_time = month_weekday(df_total)
    df_norm = normalization(df_time)
    load(df_norm)

etl()
