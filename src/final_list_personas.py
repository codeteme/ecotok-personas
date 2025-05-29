import os
import json
from datetime import datetime
from openai import OpenAI
import tiktoken

# === CONFIG ===
username = "sambentley"
threshold = 5000
number_of_personas = 5

input_dir = "../data/processed"
latest_file = sorted([f for f in os.listdir(input_dir) if f.startswith(f"{username}_persona_batch_results_>{threshold}_comments") and f.endswith(".jsonl")])[-1]
input_path = os.path.join(input_dir, latest_file)
print(f"Reading file {input_path}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"../data/processed/{username}_final_grouped_personas_{threshold}_comments_{number_of_personas}_personas_{timestamp}.txt"

MODEL = "gpt-4o"
TOKEN_LIMIT = 40000  # safe limit for GPT-4o
client = OpenAI()

def count_tokens(text, model="gpt-4o"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def load_clean_personas(file_path):
    all_contents = []
    with open(file_path, "r") as f:
        for i, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                if data.get("response", {}).get("status_code") == 200:
                    content = data["response"]["body"]["choices"][0]["message"]["content"]
                    if content:
                        all_contents.append(content.strip())
            except Exception as e:
                print(f"Error in line {i}: {e}")
    return all_contents

def chunk_content(contents, model, token_limit):
    chunks = []
    current_chunk, current_tokens = [], 0

    for content in contents:
        tokens = count_tokens(content, model)
        if current_tokens + tokens > token_limit:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [content]
            current_tokens = tokens
        else:
            current_chunk.append(content)
            current_tokens += tokens

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    return chunks

def send_to_openai(chunks, number_of_personas):
    all_outputs = []

    for i, chunk in enumerate(chunks, 1):
        print(f"Sending chunk {i} to OpenAI...")
        messages = [
            {"role": "system", "content": "You are an expert in synthesizing audience personas."},
            {"role": "user", "content": f"""Here are multiple sets of personas generated from different text batches. 
Some personas are likely similar or overlapping.

Your task:
- Group and merge similar personas across all batches.
- Eliminate redundancy.
- Produce a final, distinct set of representative personas that summarize the full dataset.
- Produce {number_of_personas} personas

Here is the input:\n\n{chunk}"""}
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3
        )

        result = response.choices[0].message.content.strip()
        all_outputs.append(f"=== Final Persona Group {i} ===\n{result}")

    return "\n\n".join(all_outputs)

# === RUN ===
raw_contents = load_clean_personas(input_path)
chunks = chunk_content(raw_contents, MODEL, TOKEN_LIMIT)
final_personas = send_to_openai(chunks, number_of_personas)

# Save result
with open(output_file, "w") as f:
    f.write(final_personas)

print(f"Final grouped personas saved to: {output_file}")