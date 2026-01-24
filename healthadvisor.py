import pandas as pd

cbc = pd.read_excel("cbc information.xlsx")
diabetes = pd.read_csv("diabetes_prediction_dataset.csv")

print(cbc.head())
print(diabetes.head())
