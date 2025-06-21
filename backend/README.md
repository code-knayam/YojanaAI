# YojanaAI Backend

YojanaAI is an OpenAI-powered FastAPI backend that helps users discover relevant government schemes in India. It uses advanced language models for query understanding and semantic search, and a local ChromaDB vector database for fast, accurate recommendations.

## 🏗️ Architecture
- **FastAPI**: REST API framework
- **OpenAI GPT-4o**: Entity extraction, reasoning, and embeddings
- **ChromaDB**: Persistent vector database for semantic search
- **Redis**: Used for rate limiting (via fastapi-limiter)
- **Endpoints**:
  - `POST /recommend`: Given a conversation history and user input, returns top matching schemes with reasons and links
  - `POST /reindex`: Rebuilds the scheme embeddings index
  - `GET /health`: Health check

## 📂 File Structure
- `main.py` — FastAPI app, endpoints, and middleware
- `core/embedding_search.py` — OpenAI embedding and ChromaDB logic
- `core/utils.py` — Scheme loading and helpers
- `service/recommendation.py` — Main recommendation logic
- `schemes.json` — Local database of government schemes
- `render.yaml` — Render.com deployment config

## 🚀 Local Development

1. **Clone the repo**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   - `OPENAI_API_KEY` (required)
   - `REDIS_URL` (for rate limiting, e.g. `redis://localhost:6379/0`)

4. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```
   
5. **Test the API**
   ```bash
   curl -X POST "http://127.0.0.1:8000/recommend" \
        -H "Content-Type: application/json" \
        -d '{"conversation_history": ["I want a loan for dairy business"], "current_input": "in Madhya Pradesh"}'
   ```

## ☁️ Deployment (Render.com)
- See `render.yaml` for service definition
- Set `OPENAI_API_KEY` and `REDIS_URL` as environment variables in Render dashboard
- ChromaDB is persisted on a mounted disk
- App is started with:
  ```
  uvicorn main:app --host 0.0.0.0 --port 8000
  ```

## 🧠 How It Works
- User query is received via `/recommend`
- OpenAI GPT-4o extracts entities and intent
- Query is embedded and matched against schemes in ChromaDB
- Top matches are returned with reasons and links
- Rate limiting is enforced via Redis

## 🤝 Contributing
See [../../CONTRIBUTIONS.md](../../CONTRIBUTIONS.md) for guidelines. 