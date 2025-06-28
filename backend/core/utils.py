import json
from typing import List, Dict, Tuple
import re

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

def clean_text_field(text: str) -> str:
    """
    Cleans a scheme-related text field by:
    - Removing markdown (**bold**, *italic*)
    - Replacing <br> tags and newlines with space
    - Flattening markdown links
    - Removing list bullets and numbers
    - Normalizing whitespace
    """
    if not text or not isinstance(text, str):
        return ""

    # Remove markdown bold/italic
    text = re.sub(r"[*_]{1,3}", "", text)

    # Replace markdown links [text](url) → text (url)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1 ( \2 )", text)

    # Remove HTML <br> tags
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)

    # Remove list bullets, dashes, or numbered lists at line start
    text = re.sub(r"^\s*(\d+\.\s*|[-•]\s*)", "", text, flags=re.MULTILINE)

    # Remove newlines and tabs
    text = re.sub(r"\s*[\n\r\t]+\s*", " ", text)

    # Collapse multiple spaces
    return re.sub(r"\s+", " ", text).strip()

def get_age_text(age_limits: dict) -> str:
    """
    Convert ageLimits dict into a readable string.
    Example: {"pwd": {"min_age": 10, "max_age": 100}} → "Eligible age: 10 to 100 for PWD"
    """
    if not age_limits:
        return ""
    
    age_parts = []
    for key, limits in age_limits.items():
        min_age = limits.get("min_age")
        max_age = limits.get("max_age")
        if min_age is not None and max_age is not None:
            age_parts.append(f"{key.upper()} : {min_age} to {max_age}")
        elif min_age is not None:
            age_parts.append(f"{key.upper()} : {min_age}+")
        elif max_age is not None:
            age_parts.append(f"{key.upper()} : under {max_age}")
    
    return "Eligible age: " + ", ".join(age_parts)


def prepare_scheme_for_metadata(scheme: dict) -> dict:
    """
    Prepares a scheme object for ChromaDB metadata.
    - Flattens or stringifies all non-primitive fields
    - Extracts readable age text
    """
    def is_primitive(val):
        return isinstance(val, (str, int, float, bool))

    # Copy original scheme to avoid mutation
    metadata = dict(scheme)

    # Flatten ageLimits to a readable string
    age_limits = scheme.get("ageLimits", {})
    if isinstance(age_limits, dict):
        metadata["ageText"] = get_age_text(age_limits)  # e.g., "PWD: 10–100"
        del metadata["ageLimits"]

    # Clean up applicationProcess list
    if isinstance(scheme.get("applicationProcess"), list):
        metadata["applicationProcess"] = " ".join(
            clean_text_field(step) for step in scheme["applicationProcess"]
        )

    # Convert list of tags, category, beneficiaries into comma-separated strings
    for key in ["tags", "category", "beneficiaries"]:
        if isinstance(scheme.get(key), list):
            metadata[key] = ", ".join(map(str, scheme[key]))

    # Convert links list of dicts to single string
    if isinstance(scheme.get("links"), list):
        metadata["links"] = " | ".join(
            f"{link.get('title')}: {link.get('url')}" for link in scheme["links"]
        )

    # Remove any remaining non-primitives (dicts/lists)
    for key, value in list(metadata.items()):
        if not is_primitive(value):
            metadata[key] = str(value)

    return metadata