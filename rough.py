import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv")

# for i in range(df.shape[0]):
#   /  row=df.iloc[i,:].values
print(df.shape)