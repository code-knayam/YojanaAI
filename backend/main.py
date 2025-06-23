import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from service.recommendation import get_scheme_response
from service.reindex import load_schemes
from core.embedding_search import index_schemes
from contextlib import asynccontextmanager
from agents import set_tracing_export_api_key
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from core.firebase_auth import verify_firebase_token
from core.settings import settings

set_tracing_export_api_key(settings.OPENAI_API_KEY)

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_conn = redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    await FastAPILimiter.init(redis_conn)
    yield
    
# FastAPI app setup
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yojanaai.web.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


class SchemeQuery(BaseModel):
    conversation_history: List[str]
    current_input: Optional[str] = ""

# API endpoint
@app.post("/recommend", dependencies=[
    Depends(RateLimiter(times=5, seconds=60)),       # 5 requests per minute
    Depends(RateLimiter(times=50, seconds=86400))    # 20 requests per day
])
async def refine_endpoint(payload: SchemeQuery, user=Depends(verify_firebase_token)):
    try:        
        return await get_scheme_response(payload.conversation_history, payload.current_input)
    except Exception as e:
        raise HTTPException(status_code=200, detail=str(e))

# Re-indexing endpoint
@app.post("/reindex", dependencies=[
    Depends(RateLimiter(times=1, seconds=86400))    # 1 request per day
])
async def trigger_reindex(user=Depends(verify_firebase_token)):
    try:
        schemes = load_schemes()
        await index_schemes(schemes, force_reindex=True)
        return {"message": "Re-indexing complete."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health
@app.get("/health")
async def health_check():
    return {"status": "OK"}