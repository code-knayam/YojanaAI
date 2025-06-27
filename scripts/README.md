# YojanaAI Scheme Scraper Scripts

This directory contains scripts to fetch and process government scheme data from the myscheme.gov.in API.

## Features
- Fetch all available schemes and store them in JSON format
- Fetch detailed information for each scheme in batches
- Handles batching and rate limiting for API calls
- Stores output in organized folders

## Setup

1. **Install dependencies:**
   ```sh
   npm install
   ```
2. **(Optional) Configure Environment:**
   - If you want to use a custom API key, update the `getHeaders` function or use a `.env` file and `dotenv`.

## Usage

### Using npm scripts (recommended)

- **Fetch all schemes:**
  ```sh
  npm run fetch:schemes
  ```
- **Fetch scheme details:**
  ```sh
  npm run fetch:details
  ```

## Output Structure
- `data/schemes.json` — All fetched schemes (array)
- `data/scheme-details/` — Folder containing detailed info for each batch

## Notes
- The script respects API rate limits by batching requests.
- If any API call in a batch fails, further batches are not executed.
- Requires Node.js 18+ and TypeScript.

## License
MIT (see [LICENSE.md](LICENSE.md))
 