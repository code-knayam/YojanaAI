# service/recommendation.py
import json
import logging
from typing import List, Dict, Union
from agents import Agent, Runner
from core.prompts import build_prompt, build_decision_prompt, SYSTEM_PROMPT, DECISION_PROMPT
from core.utils import load_schemes, MODEL
from core.embedding_search import query_schemes
from typing import Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_matched_schemes(agent_output: str) -> Tuple[str, List[Dict[str, any]]]:
    cleaned_output = agent_output.strip()
    if cleaned_output.startswith("```json"):
        cleaned_output = cleaned_output.removeprefix("```json").removesuffix("```").strip()
    elif cleaned_output.startswith("```"):
        cleaned_output = cleaned_output.removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(cleaned_output)
        if isinstance(parsed, dict) and "message" in parsed and "schemes" in parsed:
            return parsed["message"], parsed["schemes"]
        elif isinstance(parsed, list):
            return "Here are some schemes that match your requirement:", parsed
        else:
            raise ValueError("Unexpected format")
    except Exception as e:
        raise ValueError(f"Failed to parse agent output: {str(e)}")


async def get_followup_question(query: str, matched_schemes: List[Dict[str, any]]) -> Union[str, None]:
    decision_agent = Agent(
        name="Follow-up Decision Agent",
        instructions=DECISION_PROMPT,
        model=MODEL,
        tools=[],
    )

    summarized_schemes = [
        {"name": s["name"], "description": s.get("description", ""), "category": s.get("category", "")}
        for s in matched_schemes[:10]
    ]

    decision_prompt = build_decision_prompt(query, summarized_schemes)
    logger.info(f"Follow-up Decision Prompt Token Length: {len(decision_prompt)}")
    decision_response = await Runner.run(decision_agent, decision_prompt)

    followup_question = decision_response.final_output.strip()
    return followup_question if followup_question.lower() != "null" else None


async def find_matching_schemes(query: str) -> Dict[str, Union[str, List[Dict[str, any]]]]:
    matched_schemes = await query_schemes(query, top_k=25)
    logger.info(f"Initial matched scheme count: {len(matched_schemes)}")

    matcher_agent = Agent(
        name="Scheme Recommendation Agent",
        instructions=SYSTEM_PROMPT,
        model=MODEL,
        tools=[]
    )

    summarized_schemes = [
        {"name": s["name"], "description": s.get("description", ""), "category": s.get("category", "")}
        for s in matched_schemes[:10]
    ]

    matching_prompt = build_prompt(query, summarized_schemes)
    logger.info(f"Recommendation Prompt Token Length: {len(matching_prompt)}")
    match_response = await Runner.run(matcher_agent, matching_prompt)

    try:
        message, parsed_schemes = parse_matched_schemes(match_response.final_output)
        logger.info(f"Final schemes returned: {len(parsed_schemes)}")

        if len(parsed_schemes) > 10:
            followup_question = await get_followup_question(query, parsed_schemes)
            if followup_question:
                logger.info("Triggering follow-up question flow.")
                return {
                    "followup_needed": True,
                    "question": followup_question,
                    "top_matches": parsed_schemes[:5]
                }

        return {
            "message": message,
            "results": parsed_schemes
        }

    except Exception as e:
        logger.error(f"Error parsing agent response: {str(e)}")
        raise ValueError(f"Failed to parse response: {str(e)}")


async def refine_results(original_query: str, followup_answer: str) -> List[Dict[str, any]]:
    combined_query = f"{original_query}. Additional context: {followup_answer}"
    result = await find_matching_schemes(combined_query)
    return result.get("results", [])
