import os
from openai import OpenAI
from datetime import datetime

# === CONFIG ===
username = "jacobsimonsays"
threshold = 5000

batch_input_dir = "../data/intermediate"
latest_file = sorted([f for f in os.listdir(batch_input_dir) if f.startswith(f"{username}_persona_batch_input_>{threshold}") and f.endswith(".jsonl")])[-1]
input_path = os.path.join(batch_input_dir, latest_file)
print(input_path)

# Initialize OpenAI client
client = OpenAI()

print(f"Uploading file: {input_path}")

# === Upload input file ===
with open(input_path, "rb") as f:
    uploaded_file = client.files.create(file=f, purpose="batch")

print(f"File uploaded: {uploaded_file.id}")

# === Submit batch job ===
batch = client.batches.create(
    input_file_id=uploaded_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"
)

# === Output status ===
created_at = datetime.fromtimestamp(batch.created_at).strftime("%Y-%m-%d %H:%M:%S")
print("\n Batch Job Submitted")
print(f" Batch ID: {batch.id}")
print(f" Created At: {created_at}")
print(f" Status: {batch.status}")
print(f" Input File ID: {batch.input_file_id}")