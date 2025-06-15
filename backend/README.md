# Government Scheme Recommendation API

This is a FastAPI backend that recommends government schemes based on a user's query using OpenAI's GPT-4o for entity extraction and a local database for scheme matching.

## Features
- `/recommend` endpoint: Accepts a query and returns top 3 matching government schemes with reasons and links.
- Modular logic for easy extension (entity extraction, scheme matching, reasoning).
- Uses OpenAI's GPT-4o via the `openai` Python SDK.

## Setup

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your OpenAI API key**
   ```bash
   export OPENAI_API_KEY=sk-...
   # Or on Windows:
   set OPENAI_API_KEY=sk-...
   ```

4. **Run the FastAPI app**
   ```bash
   uvicorn main:app --reload
   ```

5. **Test the endpoint**
   You can use `curl`, Postman, or any HTTP client:
   ```bash
   curl -X POST "http://127.0.0.1:8000/recommend" \
        -H "Content-Type: application/json" \
        -d '{"query": "I want a ₹5 lakh loan to start a dairy business in Madhya Pradesh"}'
   ```

## File Structure
- `main.py` - FastAPI app and core logic
- `schemes.json` - Local database of government schemes
- `requirements.txt` - Python dependencies

## Extending
- Logic is modular: you can swap out or extend entity extraction, matching, or reasoning tools.
- Suitable for integration with frontend apps (e.g., React). 