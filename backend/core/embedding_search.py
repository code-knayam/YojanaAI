import uuid
import os
import json
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from openai import OpenAI

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
        scheme_id = scheme.get("id") or str(uuid.uuid4())

        if isinstance(scheme.get("keywords"), list):
            scheme["keywords"] = ", ".join(scheme["keywords"])

        text = " | ".join([
            scheme.get("name", ""),
            scheme.get("purpose", ""),
            scheme.get("eligibility", ""),
            scheme.get("sector", "")
        ])

        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        embedding = response.data[0].embedding

        collection.add(
            ids=[scheme_id],
            embeddings=[embedding],
            metadatas=[scheme]
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
