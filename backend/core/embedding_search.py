import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from core.utils import get_age_text, prepare_scheme_for_metadata

PERSIST_DIR = "./chroma_db"
SCHEMES_COLLECTION = "schemes"

# Create Chroma client and collection
chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)

# Fetch or create collection
_collection = None

def get_collection():
    global _collection
    if _collection is None:
        try:
            _collection = chroma_client.get_collection(name=SCHEMES_COLLECTION)
        except:
            _collection = chroma_client.create_collection(name=SCHEMES_COLLECTION)
    return _collection

# Rebuild index from scratch using OpenAI embeddings
async def index_schemes(schemes: List[Dict[str, any]], force_reindex: bool = False):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if force_reindex:
        try:
            chroma_client.delete_collection(name=SCHEMES_COLLECTION)
        except:
            pass

    collection = chroma_client.create_collection(name=SCHEMES_COLLECTION)

    for scheme in schemes:
        scheme_id = scheme.get("id")

        text = " | ".join(filter(None, [
            scheme.get("name", "") or "",
            scheme.get("description", "") or "",
            "Eligibility: " + (scheme.get("eligibility", "") or ""),
            get_age_text(scheme.get("ageLimits", {})) or "",
            "Tags: " + ", ".join(filter(None, scheme.get("tags", []))) if isinstance(scheme.get("tags"), list) else (scheme.get("tags") or ""),
            "Categories: " + ", ".join(scheme.get("category", [])) if isinstance(scheme.get("category"), list) else (scheme.get("category") or ""),
            "State: " + (scheme.get("state") or ""),
            "Level: " + (scheme.get("level") or ""),
            "Department: " + (scheme.get("department") or ""),
            "Benefit Type: " + (scheme.get("benefitType") or ""),
            "Agency: " + (scheme.get("agency") or ""),
            "Beneficiaries: " + ", ".join(scheme.get("beneficiaries", [])) if isinstance(scheme.get("beneficiaries"), list) else (scheme.get("beneficiaries") or "")
        ]))

        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        embedding = response.data[0].embedding

        collection.add(
            ids=[scheme_id],
            embeddings=[embedding],
            metadatas=[prepare_scheme_for_metadata(scheme)]
        )

    print("Embeddings indexed and stored successfully.")

# Semantic search using OpenAI embeddings
async def query_schemes(user_query: str, top_k: int = 10) -> List[Dict[str, any]]:
    collection = get_collection()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input=user_query,
        model="text-embedding-3-small"
    )

    query_embedding = response.data[0].embedding
    result = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    
    return result.get("metadatas", [[]])[0]
