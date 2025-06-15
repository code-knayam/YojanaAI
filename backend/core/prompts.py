# core/prompts.py
import json

SYSTEM_PROMPT = """
You are an assistant that helps users discover government schemes in India based on their needs.
Step 1: Extract purpose, location, amount, and sector from user query.
Step 2: Match these against a database of schemes.
Step 3: Return the top matching schemes with a short reason for each match.
Return the response in pure JSON format without code fences or extra text.
"""

DECISION_PROMPT = """
You are an assistant that determines whether the user query and current matched results need further clarification.
If the number of matched schemes is too high, or user input is vague or missing key details like location, sector, amount, etc., return a helpful clarifying question.
Otherwise, return null.
"""

def build_prompt(query: str, schemes: list) -> str:
    return f"""
User Query: \"{query}\"

Available Schemes:
{json.dumps(schemes, indent=2)}

Respond in the following JSON format:
[
  {{ \"name\": \"Scheme Name\", \"reason\": \"Why this scheme matches\", \"link\": \"https://example.com\" }}
]
"""

def build_decision_prompt(query: str, matches: list) -> str:
    return f"""
User Query: \"{query}\"

Top Matching Schemes:
{json.dumps(matches[:10], indent=2)}

If further clarification is needed, return a clarifying question.
If not, return null.
"""
