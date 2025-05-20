import pandas as pd 
import os

directory_path = "../data/raw/user_profiles"
all_files = os.listdir(directory_path)
csv_files = [f for f in all_files if f.endswith('.csv')]

all_df = []

for file in csv_files:
    file_path = os.path.join(directory_path, file)
    df = pd.read_csv(file_path)
    all_df.append(df)

df_concatenated = pd.concat(all_df, ignore_index=True)

print(df_concatenated)