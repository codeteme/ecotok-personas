import pandas as pd
import os

def merge_comments_by_creator(username):
    directory_path = f"../data/raw/comments/{username}"
    all_files = os.listdir(directory_path)
    csv_files = [f for f in all_files if f.endswith('.csv')]

    # print(csv_files)

    all_df = []
    for file in csv_files:
        file_path = os.path.join(directory_path, file)
        try:
            if os.path.getsize(file_path) == 0:
                print(f"Skipping empty file: {file}")
                continue
            df = pd.read_csv(file_path)
            all_df.append(df)
        except pd.errors.EmptyDataError:
            print(f"Skipping file due to parsing error (empty or corrupt): {file}")
            continue

    df_concatenated = pd.concat(all_df, ignore_index=True)
    print(df_concatenated.shape)

    output_file_path = f"../data/intermediate/comments/byCreator/{username}_{df_concatenated.shape[0]}_comments.csv"
    df_concatenated.to_csv(output_file_path)
    print(f"Total number of comments collected for {username} is {df_concatenated.shape[0]}")
    print(f"The comments for {username} are saved in {output_file_path}")

username = "sambentley"
print(merge_comments_by_creator(username))