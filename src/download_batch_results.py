import os
from openai import OpenAI
from datetime import datetime

# === CONFIG ===
username = "trashcaulin"
threshold = 5000

# === Initialize OpenAI client ===
client = OpenAI()

# Replace with your most recent or desired Batch ID
# ====================================================================================
BATCH_ID = "batch_6836f9dac2648190b1ed036701e76b08"


# === Retrieve the batch ===
batch = client.batches.retrieve(BATCH_ID)

print(f"Batch Job Status: {batch.status}")

if batch.status != "completed":
    if batch.status == "failed":
        print("Your batch job failed. Let's find out why...\n")
        if batch.error_file_id:
            print(f"Error File ID: {batch.error_file_id}")
            print("Download and inspect the error file using:")
            print(f"\nclient.files.content('{batch.error_file_id}')\n")
        else:
            print("No error file provided. The failure likely occurred during validation or setup.")
    else:
        print("Your batch job is not yet complete. Please check again later.")
    exit()

# === Download results ===
result_file_id = batch.output_file_id
result = client.files.content(result_file_id).text

# Save results to timestamped file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"../data/processed/{username}_persona_batch_results_>{threshold}_comments_{timestamp}.jsonl"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    f.write(result)

print(f"\n Results saved to: {output_path}")

