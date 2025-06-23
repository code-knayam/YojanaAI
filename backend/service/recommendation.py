import json
import logging
from typing import List, Dict, Union, Tuple
from agents import Agent, Runner
from core.prompts import build_prompt, build_decision_prompt, SYSTEM_PROMPT, DECISION_PROMPT
from core.utils import MODEL, combine_conversation, parse_matched_schemes
from core.embedding_search import query_schemes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_scheme(scheme: Dict[str, str]) -> Dict[str, str]:
    """Summarize a scheme's relevant fields for prompt use."""
    return {
        "name": scheme.get("name", ""),
        "summary": f"For {scheme.get('sector', 'varied needs')} in {scheme.get('location', 'India')}. Eligibility: {scheme.get('eligibility', 'N/A')[:80]}... Purpose: {scheme.get('purpose', '')[:100]}... Amount: {scheme.get('amount_range', 'N/A')}"
    }

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
    logger.info(f"combined query from user: {combined_query}")

    matched_schemes = await query_schemes(combined_query, top_k=25)
    logger.info(f"Initial matched scheme count: {len(matched_schemes)}")
    
    summarized_schemes = [summarize_scheme(s) for s in matched_schemes]

    if len(matched_schemes) > 10:
        decision_response_raw = await get_followup_question(combined_query, summarized_schemes)

        try:
            decision_json = json.loads(decision_response_raw)
        except Exception as e:
            logger.error("Invalid JSON from decision agent")
            raise e

        followup_needed = decision_json.get("followup_needed", False)
        show_recommendations = decision_json.get("show_recommendations", False)
        followup_question = decision_json.get("followup_question", "null")
        
        logger.info(decision_json)

        if followup_question != None:
            return {
                "followup_needed": followup_needed,
                "message": followup_question,
                "results": matched_schemes[:5] if show_recommendations else [] 
            }

    matcher_agent = Agent(
        name="Scheme Recommendation Agent",
        instructions=SYSTEM_PROMPT,
        model=MODEL,
        tools=[]
    )

    matching_prompt = build_prompt(combined_query, summarized_schemes)
    logger.info(f"Recommendation Prompt Token Length: {len(matching_prompt)}")
    match_response = await Runner.run(matcher_agent, matching_prompt)

    try:
        message, parsed_schemes, too_vague = parse_matched_schemes(match_response.final_output)
        logger.info(f"Final schemes returned: {len(parsed_schemes)}")

        return {
            "message": message,
            "results": parsed_schemes
        }

    except Exception as e:
        logger.error(f"Error parsing agent response: {str(e)}")
        raise ValueError(f"Failed to parse response: {str(e)}")
