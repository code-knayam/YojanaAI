# main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from service.recommendation import find_matching_schemes, refine_results
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
class QueryRequest(BaseModel):
    query: str

class RefineRequest(BaseModel):
    original_query: str
    followup_answer: str

# API endpoint
@app.post("/recommend")
async def recommend_endpoint(request: QueryRequest):
    try:
        result = await find_matching_schemes(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine")
async def refine_endpoint(request: RefineRequest):
    try:
        result = await refine_results(request.original_query, request.followup_answer)
        return {"results": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Re-indexing endpoint
@app.post("/reindex")
async def trigger_reindex():
    try:
        schemes = load_schemes()
        await index_schemes(schemes, force_reindex=True)
        return {"message": "Re-indexing complete."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
