import pandas as pd
import os

def merge_comments_by_creator(username):
    directory_path = f"../data/raw/comments/{username}"
    all_files = os.listdir(directory_path)
    csv_files = [f for f in all_files if f.endswith('.csv')]

    print(csv_files)

    all_df = []
    for file in csv_files:
        file_path = os.path.join(directory_path, file)
        df = pd.read_csv(file_path)
        all_df.append(df)

    df_concatenated = pd.concat(all_df, ignore_index=True)
    print(df_concatenated.shape)
    
    
    if df_concatenated.shape[0] > 5000:
        output_file_path = f"../data/raw/comments/byCreator/{username}.csv"
        df_concatenated.to_csv(output_file_path)
        print(f"Total number of comments collected for {username} is {df_concatenated.shape[0]}")
        print(f"The comments for {username} are saved in {output_file_path}")
    else: 
        print(f"Total number of comments collected - {df_concatenated.shape[0]} - for {username} is less than 5000.")

username = "climatediva"
print(merge_comments_by_creator(username))