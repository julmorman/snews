# The Weekly Loop

The Weekly Loop is a news curation and presentation system designed for schools. It aims to bridge the gap between global information and a teenage audience by providing a rotating news summary for common area displays (screens/projectors) and a companion website for deeper dives.

## Project Goal

The primary objective is to create an automated yet human-curated weekly news cycle. It focuses on four key categories:
- Geopolitics
- National (Argentina)
- Science
- Sustainability

The system generates high-impact summaries for visual loops and provides a detailed hub where students can contrast different sources, fostering critical thinking.

## Technical Stack

- **Web Interface:** [Astro](https://astro.build/) (Static Site Generator).
- **Hosting:** [Vercel](https://vercel.com/).

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18.0.0 or higher)

### Installation

1. Navigate to the project directory:
   ```bash
   cd snews
   ```

2. Install web dependencies:
   ```bash
   npm install
   ```

### Running the Project

#### 1. Start the Web Dashboard
Launch the Astro development server to preview the site:
```bash
npm run dev
```
The site will be available at `http://localhost:4321`.

### Project Structure

- `src/`: Astro components and pages for the web interface.

## Agent Steps (Workflow)

### 1. Data Reception

The agent will receive the news information (via a link to a public Google Sheet or direct text). The data is presented in columns in the following order: `section`, `title`, `image` (if applicable; otherwise, the agent will search for an image that matches the news item), and `sources` (unlimited amount).

### 2. Content Creation (JSON)

Create a new file in `src/content/news/` following the `week-XX.json` pattern.

* **Important:** Maintain the exact format of `week-01.json`.
* **ID:** The ID for each news item must be unique and descriptive (e.g., `energy-crisis-2026`).

### 3. Updating References

For the site to display the new week as the "current" one, the agent must modify:

* In `src/pages/ultima.astro`: Change the import line:
```astro
import data from '../content/news/week-XX.json';

```


* In `src/pages/presentacion.astro`: Change the import line:
```astro
import data from '../content/news/week-XX.json';

```



### 4. Verification

The file `src/pages/archivo.astro` will automatically detect the new JSON file thanks to `import.meta.glob`. No editing is required.

---

## Agent Rules

* **Do Not Rewrite:** Do not modify the logic of the `.astro` files beyond the imports.
* **Formatting:** Ensure that the JSON is valid and follows the existing field structure.
* **Surgical Edits:** Use the `replace` tool to change *only* the import line within the `.astro` files.
