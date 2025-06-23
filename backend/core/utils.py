import json
from typing import List, Dict, Tuple

SCHEMES_DB_PATH = "schemes.json"
MODEL = "gpt-4o-mini"
EMBEDDINGS_MODEL = "text-embedding-3-small"

def parse_matched_schemes(agent_output: str) -> Tuple[str, List[Dict[str, any]], bool]:
    cleaned_output = agent_output.strip()
    if cleaned_output.startswith("```json"):
        cleaned_output = cleaned_output.removeprefix("```json").removesuffix("```").strip()
    elif cleaned_output.startswith("```"):
        cleaned_output = cleaned_output.removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(cleaned_output)
        if isinstance(parsed, dict) and "message" in parsed and "schemes" in parsed:
            return parsed["message"], parsed["schemes"], parsed.get("too_vague", False)
        elif isinstance(parsed, list):
            return "Here are some schemes that match your requirement:", parsed, False
        else:
            raise ValueError("Unexpected format")
    except Exception as e:
        raise ValueError(f"Failed to parse agent output: {str(e)}")

def combine_conversation(history: List[str], current_input: str) -> str:
    return ". ".join(history + [current_input]) if current_input else ". ".join(history)