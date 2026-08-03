import os
import sys
import re
import csv
import json
import argparse
import logging
import warnings
import unicodedata
from pathlib import Path
from urllib.parse import urlparse
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
SRC_GLOSSARY_PATH = Path("src/content/glosario")
MAX_SOURCE_COLUMNS = 8
MAX_GLOSSARY_SOURCE_COLUMNS = 4

# CSV columns: section, title, image, source_1..source_8,
# glossary_term, glossary_image, glossary_source_1..glossary_source_4
CSV_COLUMN_COUNT = 3 + MAX_SOURCE_COLUMNS + 2 + MAX_GLOSSARY_SOURCE_COLUMNS

def get_next_day_date():
    """Returns tomorrow's date in Spanish format like '4 de Junio'"""
    tomorrow = datetime.now() + timedelta(days=1)
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    return f"{tomorrow.day} de {months[tomorrow.month - 1]}"

def slugify(text):
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def source_name_from_url(url):
    try:
        return urlparse(url).hostname.replace('www.', '')
    except (AttributeError, ValueError):
        return url

NEWS_PROMPT_TEMPLATE = """
Please generate a new edition for Week {week_num} based on the data provided in {csv_name}.

CSV Content (columns: section, title, image, then up to {max_sources} source URLs):
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
9. ORDER: Return exactly one news item per CSV row, in the SAME ORDER as the rows above. Do not skip, merge or reorder rows.

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

GLOSSARY_PROMPT_TEMPLATE = """
Write a glossary entry explaining "{term}" for Argentine high school students (teenagers) who are reading a weekly news site called The Loop.
This term is being referenced from a news story about: "{news_title}".

STRICT RULES:
1. Write in Spanish (Argentina), in a neutral and objective tone, assuming the reader has never heard of this before.
2. Do NOT use em dashes (—) anywhere in the text. Rewrite around them using commas, parentheses, or separate sentences instead.
3. Produce between 2 and 4 sections. Each section may have a short "heading" (like a question, e.g. "¿Qué es?") and must have a "text" field.
4. Inside "text": start a line with "* " (asterisk followed by a space) for a bullet point, and wrap bold phrases in "**like this**". Do not start a non-bullet paragraph with "**" as the very first two characters of the line.
5. Ground the explanation in the general topic of these reference sources, without inventing specific statistics, dates, or quotes you are not confident about: {sources_list}

Return ONLY a raw JSON object with this exact shape:
{{
  "short_description": "one sentence, no more than 30 words, no em dashes",
  "sections": [
    {{ "heading": "...", "text": "..." }}
  ]
}}
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

def parse_csv_rows(csv_path):
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for raw in reader:
            if not raw or not raw[0].strip():
                continue
            raw = (raw + [''] * CSV_COLUMN_COUNT)[:CSV_COLUMN_COUNT]
            sources = [s.strip() for s in raw[3:3 + MAX_SOURCE_COLUMNS] if s.strip()]
            glossary_sources_start = 3 + MAX_SOURCE_COLUMNS + 2
            glossary_sources = [
                s.strip() for s in raw[glossary_sources_start:glossary_sources_start + MAX_GLOSSARY_SOURCE_COLUMNS]
                if s.strip()
            ]
            rows.append({
                'section': raw[0].strip(),
                'title': raw[1].strip(),
                'image': raw[2].strip(),
                'sources': sources,
                'glossary_term': raw[3 + MAX_SOURCE_COLUMNS].strip(),
                'glossary_image': raw[3 + MAX_SOURCE_COLUMNS + 1].strip(),
                'glossary_sources': glossary_sources,
            })
    return rows

def build_news_csv_block(rows):
    lines = []
    for r in rows:
        lines.append(','.join([r['section'], r['title'], r['image'], *r['sources']]))
    return '\n'.join(lines)

def load_existing_glossary():
    """Returns {slug: term} for every entry already in src/content/glosario/."""
    existing = {}
    if SRC_GLOSSARY_PATH.exists():
        for f in SRC_GLOSSARY_PATH.glob('*.json'):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
                existing[data['id']] = data['term']
            except (json.JSONDecodeError, KeyError):
                logger.warning(f"No se pudo leer {f} como entrada de glosario válida.")
    return existing

def ensure_glossary_entries(rows, model):
    """For each row with a glossary_term, link to an existing entry or generate a new one.
    Returns a list (parallel to `rows`) of lists of slugs to attach as related_terms."""
    existing = load_existing_glossary()
    if existing:
        logger.info("Términos de glosario existentes: " + ", ".join(f"{term} ({slug})" for slug, term in existing.items()))

    row_slugs = []
    for row in rows:
        slugs_for_row = []
        term_names = [t.strip() for t in row['glossary_term'].split('|') if t.strip()]

        for term_name in term_names:
            slug = slugify(term_name)
            if not slug:
                continue

            if slug in existing:
                logger.info(f"'{term_name}' ya existe en el glosario ({slug}), se enlaza sin recrear.")
                slugs_for_row.append(slug)
                continue

            if not row['glossary_sources']:
                logger.warning(f"'{term_name}' no tiene fuentes en la columna de glosario (C14): se omite, no se puede crear.")
                continue

            if len(row['glossary_sources']) < 3:
                logger.warning(f"'{term_name}' tiene menos de 3 fuentes ({len(row['glossary_sources'])}). Se recomienda agregar más.")
            if any('wikipedia.org' in s for s in row['glossary_sources']):
                logger.warning(f"'{term_name}' usa Wikipedia como fuente. La convención del proyecto pide evitarla.")

            logger.info(f"Generando entrada nueva de glosario para '{term_name}'...")
            prompt = GLOSSARY_PROMPT_TEMPLATE.format(
                term=term_name,
                news_title=row['title'],
                sources_list='; '.join(row['glossary_sources']),
            )
            response = model.generate_content(prompt)
            content = response.text
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            json_str = json_match.group(1) if json_match else content.strip()
            generated = json.loads(json_str)

            entry = {
                'id': slug,
                'term': term_name,
                'short_description': generated['short_description'],
                'sections': generated['sections'],
                'images': [{'url': row['glossary_image']}] if row['glossary_image'] else [],
                'sources': [{'name': source_name_from_url(u), 'url': u} for u in row['glossary_sources']],
            }

            SRC_GLOSSARY_PATH.mkdir(parents=True, exist_ok=True)
            out_path = SRC_GLOSSARY_PATH / f"{slug}.json"
            out_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding='utf-8')
            logger.info(f"Creado {out_path}")

            existing[slug] = term_name
            slugs_for_row.append(slug)

        row_slugs.append(slugs_for_row)
    return row_slugs

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

    try:
        rows = parse_csv_rows(csv_path)
        if not rows:
            logger.error("No se encontraron filas de datos en el CSV.")
            return

        row_slugs = ensure_glossary_entries(rows, model)

        logger.info(f"Generando contenido de noticias para la Semana {week_num} con Gemini...")
        prompt = NEWS_PROMPT_TEMPLATE.format(
            week_num=week_num,
            csv_name=csv_path.name,
            csv_content=build_news_csv_block(rows),
            max_sources=MAX_SOURCE_COLUMNS,
            json_file_name_stem=json_file_name_stem,
            next_day_date=get_next_day_date()
        )

        response = model.generate_content(prompt)
        content = response.text

        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        json_str = json_match.group(1) if json_match else content.strip()

        parsed_json = json.loads(json_str)
        news_items = parsed_json.get('news', [])

        if len(news_items) != len(rows):
            logger.warning("La cantidad de noticias generadas no coincide con las filas del CSV. Revisá related_terms a mano.")
        else:
            for item, slugs in zip(news_items, row_slugs):
                if slugs:
                    item['related_terms'] = slugs

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
