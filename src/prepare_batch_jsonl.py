import pandas as pd
import tiktoken
import json
import os
from datetime import datetime

# === CONFIG ===
username = "trashcaulin"
threshold = 5000

input_merged_directory = "../data/intermediate/comments/byCreator"
input_csv_files = [
    f for f in os.listdir(input_merged_directory)
    if f.startswith(f"{username}_") and f.endswith("_comments.csv")
]
matching_files = []

for csv_file in input_csv_files:
    try:
        comments_collected = int(csv_file.split('_')[1])
        if threshold <= comments_collected <= threshold + 1000:
            matching_files.append(csv_file)
    except (IndexError, ValueError):
        print(f"Skipping malformed filename: {csv_file}")

if not matching_files:
    print("No file matches your parameters.")
else:
    for file in matching_files:
        input_merged_file = os.path.join(input_merged_directory, file)
        print(f"File to be processed: {input_merged_file}")

model = "gpt-4o-mini"
encoding = tiktoken.encoding_for_model(model)
max_input_tokens = 20000  # keep well below 30,000 token TPM cap

# Timestamped output file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_jsonl = f"../data/intermediate/{username}_persona_batch_input_>{threshold}_comments_{timestamp}.jsonl"

# === Load comments ===
df = pd.read_csv(input_merged_file)
comments = df["text"].dropna().unique().tolist()

# === Token-safe chunking ===
chunks = []
current_chunk = []
current_tokens = 0

for comment in comments:
    text = f"- {comment}"
    tokens = len(encoding.encode(text))
    if current_tokens + tokens > max_input_tokens:
        chunks.append(current_chunk)
        current_chunk = []
        current_tokens = 0
    current_chunk.append(text)
    current_tokens += tokens

if current_chunk:
    chunks.append(current_chunk)

# === Write .jsonl file ===
os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
with open(output_jsonl, "w") as f:
    for i, chunk in enumerate(chunks):
        prompt = f"""You are an audience analyst working to understand TikTokers followers of {username} on TikTok.

Here is a list of comments made on the TikTokers videos:

{chr(10).join(chunk)}

Your task is to:
1. Identify the **distinct fan personas** represented in these comments.
2. For **each persona**, provide:
   - A fictional name
   - Estimated age range and gender (only if hinted)
   - Likely occupation or life stage (only if hinted)
   - Interests, motivations, and personality traits (only if hinted)
   - Attitude toward the the TikToker (only if hinted)
   - Style or tone of writing (only if hinted)
   - **3–5 example comments from the list above** that fit this persona. Do not make up examples. The examples must exist in the list.

The number of personas is up to you—identify as many as are meaningfully distinct based on the content and tone of the comments. 
Do not make up comments—only use real examples from the list provided."""

        request = {
            "custom_id": f"batch-{i+1}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 4000
            }
        }
        f.write(json.dumps(request) + "\n")

print(f" Created {len(chunks)} token-safe GPT batch requests.")
print(f" Output file saved to: {output_jsonl}")