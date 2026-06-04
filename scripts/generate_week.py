import os
import sys
import re
import json
import argparse
import logging
import warnings
from pathlib import Path

# Try to load environment variables from .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Suppress the deprecation warning for the old SDK until the environment is updated
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

import google.generativeai as genai

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
SRC_NEWS_PATH = Path("src/content/news")

PROMPT_TEMPLATE = """
Please generate a new edition for Week {week_num} based on the data provided in {csv_name}.

CSV Content:
{csv_content}

Follow these steps:
1. Read the CSV to extract the news items.
2. Create a JSON structure for src/content/news/{json_file_name}.

CRITICAL: The JSON must strictly follow this structure and use these exact keys:
{{
  "id": "{json_file_name_stem}",
  "date": "Full date description in Spanish (e.g. 30 de Mayo)",
  "funny_title": "Semana {week_num}",
  "news": [
    {{
      "id": "unique-kebab-case-id",
      "category": "must be one of: geopolítica, nacional, ciencias, sustentabilidad",
      "title": "Original Spanish Title from CSV",
      "short_summary": "Original Spanish Short Summary or a concise version",
      "image": "Exact URL from CSV",
      "context": "* Point 1\\n* Point 2\\n* Point 3",
      "extended_context": "Longer explanation in Spanish based on sources...",
      "links": [
        {{ "name": "Source Name (e.g. BBC, El País)", "url": "URL from CSV" }}
      ]
    }}
  ]
}}

Provide ONLY the raw JSON content.
"""

def setup_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set. Please set it in your environment or .env file.")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    # Default to gemini-2.5-flash as discovered in the environment
    return genai.GenerativeModel('gemini-2.5-flash')

def get_week_number(filename):
    """Extracts week number from filename like 'news_week_02.csv' or 'week-02.csv'"""
    match = re.search(r'(\d+)', filename)
    if match:
        return match.group(1).zfill(2)
    return None

def generate_week(csv_path):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return

    week_num = get_week_number(csv_path.name)
    if not week_num:
        logger.error("Could not determine week number from filename. Please use format 'week-XX.csv'.")
        return

    json_file_name = f"week-{week_num}.json"
    json_file_name_stem = f"week-{week_num}"
    json_path = SRC_NEWS_PATH / json_file_name

    # Idempotency check
    if json_path.exists():
        logger.info(f"Week {week_num} already exists at {json_path}. Skipping generation.")
        # Even if it exists, we might want to check if it's valid, but for now we trust it
        return

    model = setup_gemini()
    logger.info(f"Generating content for Week {week_num} using Gemini...")

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()

        prompt = PROMPT_TEMPLATE.format(
            week_num=week_num,
            csv_name=csv_path.name,
            csv_content=csv_content,
            json_file_name=json_file_name,
            json_file_name_stem=json_file_name_stem
        )

        try:
            response = model.generate_content(prompt)
        except Exception as e:
            if "404" in str(e):
                logger.warning("Primary model not found. Attempting to find an alternative...")
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                if available_models:
                    alt_model_name = available_models[0].split('/')[-1]
                    logger.info(f"Falling back to model: {alt_model_name}")
                    alt_model = genai.GenerativeModel(alt_model_name)
                    response = alt_model.generate_content(prompt)
                else:
                    raise e
            else:
                raise e

        content = response.text
        
        # Extract JSON from markdown blocks if present
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        json_str = json_match.group(1) if json_match else content.strip()

        # Validate and format JSON
        parsed_json = json.loads(json_str)
        
        # Ensure directory exists
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully created {json_path}")
        logger.info("Astro content will update automatically via Content Collections.")

    except json.JSONDecodeError:
        logger.error("Gemini returned invalid JSON. Check the output manually.")
        logger.debug(f"Raw response: {content}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate Week generation from CSV using Gemini API.")
    parser.add_argument("csv_file", help="Path to the CSV file (e.g., week-02.csv)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)

    generate_week(args.csv_file)
