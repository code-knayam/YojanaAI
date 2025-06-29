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
    """Summarize a scheme's relevant fields for use in the Recommendation Agent prompt."""
    
    # Fallback helpers
    def safe(val, fallback="N/A"):
        return val if val else fallback

    def short(text, limit=100):
        return text[:limit].strip() + ("..." if len(text) > limit else "")
    
    # Compose the summary
    summary = (
        f"Id: {scheme.get('id')} "
        f"{scheme.get('name', 'Unnamed Scheme')} "
        f"is a {safe(scheme.get('benefitType'), 'benefit')} scheme by the "
        f"{safe(scheme.get('department'), 'concerned department')} in {safe(scheme.get('state'), 'India')}.\n"
        f"Target group: {', '.join(scheme.get('beneficiaries', [])) if isinstance(scheme.get('beneficiaries'), list) else safe(scheme.get('beneficiaries'))}.\n"
        f"Eligibility: {short(scheme.get('eligibility', 'N/A'), 150)}\n"
        f"Purpose: {short(scheme.get('description') or scheme.get('purpose'), 200)}\n"
        f"Benefit Amount: {safe(scheme.get('amount_range')) or safe(scheme.get('benefits'), 'N/A')}"
    )

    return {
        "name": scheme.get("name", "Unnamed Scheme"),
        "summary": summary
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
        message, parsed_schemes = parse_matched_schemes(match_response.final_output)
        
        logger.info(f"Final schemes returned: {len(parsed_schemes)}")

        # Create a mapping of scheme IDs to full scheme details
        scheme_map = {scheme.get("id"): scheme for scheme in matched_schemes}
        
        # Map parsed schemes to full scheme details using list comprehension
        mapped_schemes = [
            {**scheme_map[parsed_scheme["id"]], "reason": parsed_scheme.get("reason", "")}
            for parsed_scheme in parsed_schemes
            if parsed_scheme.get("id") in scheme_map
        ]

        return {
            "message": message,
            "results": mapped_schemes
        }

    except Exception as e:
        logger.error(f"Error parsing agent response: {str(e)}")
        raise ValueError(f"Failed to parse response: {str(e)}")
