# core/utils.py
import json
from typing import List, Dict

SCHEMES_DB_PATH = "schemes.json"
MODEL = "gpt-4o-mini"
EMBEDDINGS_MODEL = "text-embedding-3-small"

# Load schemes from file
def load_schemes() -> List[Dict[str, any]]:
    with open(SCHEMES_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
