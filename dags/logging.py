import pandas as pd

df = pd.read_csv("/home/rafael/Documents/Code2/dags/retaildata.csv")


print(df.isnull().sum())
