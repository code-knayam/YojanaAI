# service/recommendation.py
import json
import logging
from typing import List, Dict, Union, Tuple
from agents import Agent, Runner
from core.prompts import build_prompt, build_decision_prompt, SYSTEM_PROMPT, DECISION_PROMPT
from core.utils import load_schemes, MODEL
from core.embedding_search import query_schemes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

async def get_followup_question(combined_query: str, summarized_schemes: list):
    decision_agent = Agent(
        name="Follow-up Decision Agent",
        instructions=DECISION_PROMPT,
        model=MODEL,
        tools=[],
    )

    decision_prompt = build_decision_prompt(combined_query, summarized_schemes)
    logger.info(f"Follow-up Decision Prompt Token Length: {len(decision_prompt)}")
    decision_response = await Runner.run(decision_agent, decision_prompt)

    return decision_response.final_output.strip()

async def get_scheme_response(conversation_history: List[str], current_input: str) -> Dict[str, Union[str, List[Dict[str, any]]]]:
    combined_query = combine_conversation(conversation_history, current_input)
    matched_schemes = await query_schemes(combined_query, top_k=25)
    logger.info(f"Initial matched scheme count: {len(matched_schemes)}")

    matcher_agent = Agent(
        name="Scheme Recommendation Agent",
        instructions=SYSTEM_PROMPT,
        model=MODEL,
        tools=[]
    )

    summarized_schemes = [
        {"name": s["name"], "description": s.get("description", ""), "category": s.get("category", "")}
        for s in matched_schemes
    ]

    matching_prompt = build_prompt(combined_query, summarized_schemes)
    logger.info(f"Recommendation Prompt Token Length: {len(matching_prompt)}")
    match_response = await Runner.run(matcher_agent, matching_prompt)

    try:
        message, parsed_schemes, too_vague = parse_matched_schemes(match_response.final_output)
        logger.info(f"Final schemes returned: {len(parsed_schemes)}")

        if len(parsed_schemes) > 5 or too_vague:
            followup_question = await get_followup_question(combined_query, summarized_schemes)

            if followup_question.lower() != "null":
                return {
                    "followup_needed": True,
                    "message": followup_question,
                    "results": [] if too_vague else parsed_schemes[:5]
                }

        return {
            "message": message,
            "results": parsed_schemes
        }

    except Exception as e:
        logger.error(f"Error parsing agent response: {str(e)}")
        raise ValueError(f"Failed to parse response: {str(e)}")
