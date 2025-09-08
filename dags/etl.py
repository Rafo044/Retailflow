
from pandas import DataFrame
from airflow.sdk import task,dag,asset,Asset
import pandas as pd
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook




# ========   Extract Transform  Load  ===========


@asset(
    schedule="@daily",
    uri="https://raw.githubusercontent.com/Rafo044/Retailflow/refs/heads/main/data/retaildata.csv"
)
def extract(self)->DataFrame:
    df = pd.read_csv(self.uri)
    return df


@dag(
    schedule="@daily",
    start_date=datetime(2025, 10, 10),
    catchup=False,
    tags=["retail", "etl"]
)
def etl(df): #Transform
    @task()
    def handling(df : DataFrame) -> DataFrame:
        if df.isnull().any().any():
            df.drop_duplicates(subset=['invoice_no'], inplace=True)
            df.fillna({'payment_method':'Unknown', 'category':'Misc'}, inplace=True)
            return df


    @task
    def total_revinue(df : DataFrame) -> DataFrame:
        df["total_revinue"]= df["quantity"]*df["price"]
        df["average_order_value"] = df["total_revinue"] / df["invoice_no"]
        df["total_quantity_solid"] = df["quantity"].sum()
        return df

    @task
    def month_weekday(df: DataFrame) -> DataFrame:
        df["invoice_date"] = pd.to_datetime(df["invoice_date"])
        df["month"] = df["invoice_date"].dt.month
        df["weekday"] = df["invoice_date"].dt.day_name()
        return df

    @task
    def normalization(df: DataFrame) -> DataFrame:
        df["price"] = df["price"].astype(float)
        df["quantity"] = df["quantity"].astype(int)
        df["total_revinue"] = df["total_revinue"].astype(float)
        df["average_order_value"] = df["average_order_value"].astype(float)
        df["total_quantity_solid"] = df["total_quantity_solid"].astype(int)
        df['category'] = df['category'].str.strip().str.title()
        return df

    #Load
    @task
    def load(df):
        hook = MySqlHook(mysql_conn_id='retailflow')
        hook.insert_rows(table='transformed_data', rows=df.to_dict('records'))

    load(normalization(month_weekday(total_revinue(handling()))))


etl(extract())
