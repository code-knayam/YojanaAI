import json
from typing import List, Dict
from core.utils import SCHEMES_DB_PATH

def load_schemes() -> List[Dict[str, any]]:
    with open(SCHEMES_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)