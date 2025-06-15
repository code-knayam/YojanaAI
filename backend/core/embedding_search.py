# core/embedding_search.py
import uuid
import os
import json
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

PERSIST_DIR = "/app/chroma_db"
SCHEMES_COLLECTION = "schemes"

# Load local embedding model
def get_model():
    if not hasattr(get_model, "model"):
        get_model.model = SentenceTransformer("all-MiniLM-L6-v2")
    return get_model.model

# Shared Chroma client with persistence
chroma_client = chromadb.Client(Settings(
    anonymized_telemetry=False,
    persist_directory=PERSIST_DIR
))

# Get or create persistent Chroma collection
def get_collection():
    try:
        return chroma_client.get_collection(name=SCHEMES_COLLECTION)
    except:
        return chroma_client.create_collection(name=SCHEMES_COLLECTION)

# Index schemes and persist (only on demand)
async def index_schemes(schemes: List[Dict[str, any]], force_reindex: bool = False):
    if not force_reindex:
        try:
            collection = chroma_client.get_collection(name=SCHEMES_COLLECTION)
            if len(collection.get()["ids"]) > 0:
                print("Embeddings already exist. Skipping re-indexing.")
                return
        except:
            pass

    if force_reindex:
        try:
            chroma_client.delete_collection(name=SCHEMES_COLLECTION)
        except:
            pass

    collection = chroma_client.create_collection(name=SCHEMES_COLLECTION)

    for scheme in schemes:
        # Flatten any non-primitive values in metadata
        if isinstance(scheme.get("keywords"), list):
            scheme["keywords"] = ", ".join(scheme["keywords"])

        content = f"{scheme['name']} - {scheme['purpose']} - {scheme['eligibility']} - {scheme['sector']}"
        model = get_model()
        
        embedding = model.encode(content).tolist()

        collection.add(
            ids=[scheme.get("id") or str(uuid.uuid4())],
            embeddings=[embedding],
            metadatas=[scheme]
        )

    # Persist is now handled automatically if persist_directory is set
    print("Embeddings created and stored.")

# Query schemes by semantic similarity
async def query_schemes(user_query: str, top_k: int = 10) -> List[Dict[str, any]]:
    collection = get_collection()
    model = get_model()
    
    embedding = model.encode(user_query).tolist()

    result = collection.query(query_embeddings=[embedding], n_results=top_k)
    return result["metadatas"][0]
