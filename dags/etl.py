from pandas import DataFrame
from airflow.sdk import task, dag,task_group
import pandas as pd
from datetime import datetime
from io import StringIO
import requests
from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine
from log import log_decorator

url = "https://raw.githubusercontent.com/Rafo044/Retailflow/refs/heads/main/data/retaildata.csv"
conn = BaseHook.get_connection("retailflow")
conn_str = f"mysql+mysqldb://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}"
engine = create_engine(conn_str)


# ========   Extract [Data Quality Checks]  Load  ===========

@dag(
    schedule="@daily",
    start_date=datetime(2025, 1, 9),
    catchup=False,
    tags=["retail", "etl"]
)
def etl():

    #======== Extract  ===========
    #@log_decorator
    @task
    def extract() -> DataFrame:
        response = requests.get(url)
        print(response.status_code)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
        else:
            raise Exception("Failed to fetch data")
        return df

    # ---- invoice_no ----
    @log_decorator
    @task_group
    def clean_invoice_no(df: DataFrame) -> DataFrame:
        @task
        def task01(df : DataFrame):
            if df["invoice_no"].duplicated().sum() == 0:
                print("No duplicate invoice numbers found.")
            else:
                print(f"Duplicate invoice numbers found: {df['invoice_no'].duplicated().sum()}")
            return df
        @task
        def task02(df : DataFrame):
            if df['invoice_no'].str.match(r'^I\d+$').all() == True:
                print("All invoice numbers are valid.")
            else:
                print("Some invoice numbers are invalid.")
            return df
        @task
        def task03(df : DataFrame):
            if df["invoice_no"].isnull().sum() == 0:
                print("No null invoice numbers found.")
            else:
                print(f"Null invoice numbers found: {df['invoice_no'].isnull().sum()}")
            return df


        df1 = task01(df)
        df2 = task02(df1)
        df3 = task03(df2)
        return df3

    # --- customer_id ---
    @log_decorator
    @task
    def clean_customer_id(df: DataFrame) -> DataFrame:
        try:
            if 'customer_id' in df.columns:
                df['customer_id'] = df['customer_id'].astype(str).str.strip()
            return df
        except Exception as e:
            print(f"clean_customer_id error: {e}")
            return df

    # --- gender ---
    @log_decorator
    @task
    def clean_gender(df: DataFrame) -> DataFrame:
        try:
            if 'gender' in df.columns:
                df['gender'] = df['gender'].astype(str).str.strip().str.title()
                df['gender'] = df['gender'].replace({'': 'Unknown', 'Nan': 'Unknown'})
            return df
        except Exception as e:
            print(f"clean_gender error: {e}")
            return df

    # --- age ---
   # @log_decorator
    @task
    def clean_age(df: DataFrame) -> DataFrame:
        try:
            if 'age' in df.columns:
                df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(0).astype(int)
            return df
        except Exception as e:
            print(f"clean_age error: {e}")
            return df

    # --- price ---
    #@log_decorator
    @task
    def clean_price(df: DataFrame) -> DataFrame:
        try:
            if 'price' in df.columns:
                df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
            return df
        except Exception as e:
            print(f"clean_price error: {e}")
            return df

    # --- payment_method ---
    @log_decorator
    @task
    def clean_payment_method(df: DataFrame) -> DataFrame:
        try:
            if 'payment_method' in df.columns:
                df['payment_method'] = df['payment_method'].astype(str).str.strip().str.title()
                df['payment_method'] = df['payment_method'].replace({'': 'Unknown', 'Nan': 'Unknown'})
            return df
        except Exception as e:
            print(f"clean_payment_method error: {e}")
            return df

    # --- invoice_date ---
    @log_decorator
    @task
    def clean_invoice_date(df: DataFrame) -> DataFrame:
        try:
            if 'invoice_date' in df.columns:
                df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')
            return df
        except Exception as e:
            print(f"clean_invoice_date error: {e}")
            return df

    # --- shopping_mall ---
    @log_decorator
    @task
    def clean_shopping_mall(df: DataFrame) -> DataFrame:
        try:
            if 'shopping_mall' in df.columns:
                df['shopping_mall'] = df['shopping_mall'].astype(str).str.strip().str.title()
                df['shopping_mall'] = df['shopping_mall'].replace({'': 'Unknown', 'Nan': 'Unknown'})
            return df
        except Exception as e:
            print(f"clean_shopping_mall error: {e}")
            return df



    #======== Load  ===========

    @task
    def load(df: DataFrame):
        df.to_sql(
            name="retaildata",
            con=engine,
            if_exists="append",
            index=False
        )

    df_extracted = extract()
    df_invoice_no = clean_invoice_no(df_extracted)
    df_customer_id = clean_customer_id(df_invoice_no)
    df_gender = clean_gender(df_customer_id)
    df_age = clean_age(df_gender)
    df_price = clean_price(df_age)
    df_payment_method = clean_payment_method(df_price)
    df_invoice_date = clean_invoice_date(df_payment_method)
    df_shopping_mall = clean_shopping_mall(df_invoice_date)
    load(df_shopping_mall)

etl()
