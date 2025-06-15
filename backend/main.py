# main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from service.recommendation import get_scheme_response
from core.embedding_search import index_schemes
from core.utils import load_schemes
from contextlib import asynccontextmanager
from agents import set_tracing_export_api_key

# os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
set_tracing_export_api_key(os.getenv("OPENAI_API_KEY"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    schemes = load_schemes()
    await index_schemes(schemes)
    yield
    
# FastAPI app setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
class SchemeQuery(BaseModel):
    conversation_history: List[str]
    current_input: Optional[str] = ""

# API endpoint
@app.post("/recommend")
async def refine_endpoint(payload: SchemeQuery):
    try:        
        return await get_scheme_response(payload.conversation_history, payload.current_input)
    except Exception as e:
        raise HTTPException(status_code=200, detail=str(e))

# Re-indexing endpoint
@app.post("/reindex")
async def trigger_reindex():
    try:
        schemes = load_schemes()
        await index_schemes(schemes, force_reindex=True)
        return {"message": "Re-indexing complete."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "OK"}