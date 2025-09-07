
from pandas.core.reshape.encoding import DataFrame
from airflow.sdk import task,dag,asset,Asset
from pandas as pd
from airflow.models import Variable





path = Variable.get("path")

def extract():
    df = pd.read_csv(path)
    return df

def transfor():
    df = extract()



def load(df):
    df.to_csv('transformed_data.csv', index=False)
