import os
import sys
import re
import json
import argparse
import logging
import warnings
from pathlib import Path
from datetime import datetime, timedelta

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

def get_next_day_date():
    """Returns tomorrow's date in Spanish format like '4 de Junio'"""
    tomorrow = datetime.now() + timedelta(days=1)
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    return f"{tomorrow.day} de {months[tomorrow.month - 1]}"

PROMPT_TEMPLATE = """
Please generate a new edition for Week {week_num} based on the data provided in {csv_name}.

CSV Content:
{csv_content}

STANDARD OPERATING PROCEDURE (CRITICAL RULES):
1. TITLES: Must be short (max 10 words), catchy, and STRICTLY NEUTRAL/OBJECTIVE. No opinions.
2. SHORT SUMMARY (SUBTITLE): Must be DIFFERENT from the title. Do not repeat the same information. Max 15 words. Concise and complementary.
3. CONTEXT (LOOP SLIDES): EXACTLY 3 bullet points. Each bullet point MUST have between 15 and 20 words. Neither more nor less. This is vital for the visual balance of the presentation.
4. EXTENDED CONTEXT: Provide a deep-dive explanation (2-3 paragraphs) for the news detail page.
5. IMAGES: Copy the URL from the CSV EXACTLY character by character. Do NOT modify the URL parameters.
6. DATE: Use exactly "{next_day_date}".
7. WEEK TITLE: Use exactly "Semana {week_num}".
8. GRAMMAR: Perfect Spanish with all necessary accents (tildes).

JSON Structure:
{{
  "id": "{json_file_name_stem}",
  "date": "{next_day_date}",
  "funny_title": "Semana {week_num}",
  "news": [
    {{
      "id": "unique-kebab-case-id",
      "category": "must be one of: geopolítica, nacional, ciencia-ambiente, negocios-tecnologia, opinión",
      "title": "Short, objective title",
      "short_summary": "Unique, non-repetitive brief summary (max 15 words)",
      "image": "EXACT URL FROM CSV",
      "context": "* Point 1 (15-20 words)\\n* Point 2 (15-20 words)\\n* Point 3 (15-20 words)",
      "extended_context": "Detailed explanation for the news page...",
      "links": [
        {{ "name": "Source Name", "url": "URL from CSV" }}
      ]
    }}
  ]
}}

Provide ONLY the raw JSON content.
"""

def setup_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set.")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def get_week_number(filename):
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
        logger.error("Could not determine week number.")
        return

    json_file_name = f"week-{week_num}.json"
    json_file_name_stem = f"week-{week_num}"
    json_path = SRC_NEWS_PATH / json_file_name

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
            json_file_name_stem=json_file_name_stem,
            next_day_date=get_next_day_date()
        )

        response = model.generate_content(prompt)
        content = response.text
        
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        json_str = json_match.group(1) if json_match else content.strip()

        parsed_json = json.loads(json_str)
        
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully created {json_path}")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate Week generation from CSV.")
    parser.add_argument("csv_file", help="Path to the CSV file")
    args = parser.parse_args()
    generate_week(args.csv_file)
