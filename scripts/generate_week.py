import os
import sys
import re
import csv
import json
import argparse
import google.generativeai as genai
from pathlib import Path

# Setup Gemini API
# You should set GEMINI_API_KEY in your environment variables
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

def get_week_number(filename):
    """Extracts week number from filename like 'news_week_02.csv' or 'week-02.csv'"""
    match = re.search(r'(\d+)', filename)
    if match:
        return match.group(1).zfill(2)
    return None

def generate_week(csv_path):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"Error: File {csv_path} not found.")
        return

    week_num = get_week_number(csv_path.name)
    if not week_num:
        print("Error: Could not determine week number from filename. Use format 'week-XX.csv'.")
        return

    json_file_name = f"week-{week_num}.json"
    json_path = Path("src/content/news") / json_file_name

    # Idempotency check
    if json_path.exists():
        print(f"Skipping: {json_file_name} already exists. Idempotency maintained.")
        return

    print(f"Generating content for Week {week_num}...")

    # Read CSV content to include in the prompt for context (optional but helpful)
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_content = f.read()

    prompt = f"""
Please generate a new edition for Week {week_num} based on the data provided in {csv_path.name}.

CSV Content:
{csv_content}

Follow these steps:
1. Read the CSV to extract the news items.
2. Create a JSON structure for src/content/news/{json_file_name}.
    * Use English for all JSON keys (funny_title, date, news, etc.).
    * For each news item, keep the original Spanish content for title and short_summary.
    * Generate a detailed context (3 bullet points) and a longer extended_context in Spanish based on the news titles and sources provided.
    * Map the source 01, 02, and 03 columns to the links array.
3. Update the 'current' edition references:
    * In src/pages/ultima.astro, update the import to point to {json_file_name}.
    * In src/pages/presentacion.astro, update the import to point to {json_file_name}.

Provide ONLY the JSON content for the file, and I will handle the file creation and reference updates.
"""

    response = model.generate_content(prompt)
    
    # Extract JSON from response (handling potential markdown blocks)
    content = response.text
    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
    if json_match:
        json_data = json_match.group(1)
    else:
        json_data = content.strip()

    try:
        # Validate JSON
        parsed_json = json.loads(json_data)
        
        # Write the JSON file
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, indent=2, ensure_ascii=False)
        print(f"Successfully created {json_path}")

        # Update Astro files
        update_astro_references(json_file_name)

    except json.JSONDecodeError:
        print("Error: Gemini returned invalid JSON.")
        print("Response was:")
        print(content)

def update_astro_references(json_file_name):
    pages_to_update = [
        "src/pages/ultima.astro",
        "src/pages/presentacion.astro"
    ]

    for page_path in pages_to_update:
        path = Path(page_path)
        if not path.exists():
            print(f"Warning: {page_path} not found, skipping update.")
            continue

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open(path, 'w', encoding='utf-8') as f:
            for line in lines:
                # Replace import line
                # Pattern: import data from '../content/news/week-XX.json';
                new_line = re.sub(r"import data from '\.\./content/news/week-\d+\.json';", 
                                  f"import data from '../content/news/{json_file_name}';", line)
                f.write(new_line)
        
        print(f"Updated references in {page_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate Week generation from CSV using Gemini.")
    parser.add_argument("csv_file", help="Path to the CSV file (e.g., week-02.csv)")
    args = parser.parse_args()

    generate_week(args.csv_file)
