# YojanaAI

**YojanaAI** is an open-source, AI-powered platform to help users discover the most relevant government schemes in India. It combines the power of OpenAI's language models with a modern Angular frontend for a seamless, chat-based experience.

## 🚀 Vision
Empower every citizen to easily find and benefit from government schemes using conversational AI.

## 🏗️ Architecture
- **Frontend**: Angular 19, Firebase Auth, ChatGPT-inspired UI, signals for reactivity
- **Backend**: FastAPI, OpenAI GPT-4o, ChromaDB for semantic search, Redis for rate limiting
- **API**: REST endpoints for recommendations, health, and reindexing

## 📦 Monorepo Structure
```
YojanaAI/
  backend/    # FastAPI, OpenAI, ChromaDB, Redis
  frontend/   # Angular, Firebase Auth, Chat UI
```

## 🛠️ Quick Start
For detailed setup and usage instructions, see:
- [backend/README.md](backend/README.md)
- [frontend/README.md](frontend/README.md)

## ☁️ Deployment
- **Frontend:**
  - On every push to `main`, the Angular app is automatically built and deployed to Firebase Hosting via GitHub Actions ([workflow](.github/workflows/firebase-hosting-merge.yml)).
- **Backend:** See `backend/render.yaml` for Render.com config
- **Manual:** See the respective README files for manual deployment steps

## 🤝 Open Source & Contributing
We welcome contributions! See [CONTRIBUTIONS.md](CONTRIBUTIONS.md) for how to get started.

## 📄 License
MIT (see [LICENSE.md](LICENSE.md))
