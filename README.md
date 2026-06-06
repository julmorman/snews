# The Weekly Loop

The Weekly Loop is a news curation and presentation system designed for schools. It aims to bridge the gap between global information and a teenage audience by providing a rotating news summary for common area displays (screens/projectors) and a companion website for deeper dives.

## Project Goal

The primary objective is to create an automated yet human-curated weekly news cycle focusing on: Geopolitics, National (Argentina), Science, and Sustainability.

## Technical Stack

- **Web Interface:** [Astro](https://astro.build/) (Static Site Generator) with TypeScript.
- **Content Management:** Astro Content Collections (Type-safe JSON).
- **Automation:** Python 3 + Gemini AI (Google Generative AI).
- **Hosting:** [Vercel](https://vercel.com/).
- **Live Site:** [the-weekly-loop.vercel.app](https://the-weekly-loop.vercel.app)

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18.0.0 or higher)
- [Python 3](https://www.python.org/)

### Installation

1. Clone and navigate to the directory:
   ```bash
   cd the-loop
   ```

2. Install web dependencies:
   ```bash
   npm install
   ```

3. (Optional) Install Python dependencies for automation:
   ```bash
   pip install google-generativeai python-dotenv
   ```

Debian 13 notes

```bash
# Install venv support if needed
sudo apt update
sudo apt install python3-full python3-venv

# Create a virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install packages
pip install google-generativeai python-dotenv
```

### Running the Project

#### 1. Generate New Week (Automated)
Ensure your `GEMINI_API_KEY` is set in a `.env` file (see `.env.example`).

```bash
python3 scripts/generate_week.py week-02.csv
```
The script uses AI to transform your CSV data into a type-safe JSON edition and updates the site references automatically. The CSV input file must follow the schema and structure specified in [news_example.csv](./news_example.csv).

#### 2. Start the Web Dashboard
```bash
npm run dev
```
The site will be available at `http://localhost:4321`.

## Project Structure

- `src/components/`: Reusable Astro components.
- `src/config/`: Centralized site settings and constants.
- `src/content/`: Managed data editions (via Content Collections).
- `src/layouts/`: Shared page layouts.
- `src/pages/`: Website routes.
- `scripts/`: Automation and maintenance scripts.
- [news_example.csv](./news_example.csv): Reference CSV template detailing the columns and data structure required for weekly imports.

## Senior Engineering Standards Applied

- **DRY (Don't Repeat Yourself):** Centralized categories, colors, and site metadata in `src/config/constants.ts`.
- **Type Safety:** Implemented Astro Content Collections with Zod schemas for mandatory data validation.
- **Component-Based Architecture:** Logic-heavy UI elements extracted into reusable `.astro` components.
- **Robust Automation:** Python script upgraded with environment management, proper logging, and idempotent execution.
- **GitOps Workflow:** Content is versioned in Git, providing a complete history of all news editions.
