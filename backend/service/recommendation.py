# service/recommendation.py
import json
from typing import List, Dict, Union
from agents import Agent, Runner
from core.prompts import build_prompt, build_decision_prompt, SYSTEM_PROMPT, DECISION_PROMPT
from core.utils import load_schemes, MODEL
from core.embedding_search import query_schemes


def parse_matched_schemes(agent_output: str) -> List[Dict[str, any]]:
    cleaned_output = agent_output.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(cleaned_output)


async def get_followup_question(query: str, matched_schemes: List[Dict[str, any]]) -> Union[str, None]:
    decision_agent = Agent(
        name="Follow-up Decision Agent",
        instructions=DECISION_PROMPT,
        model=MODEL,
        tools=[],        
    )
    decision_prompt = build_decision_prompt(query, matched_schemes)
    decision_response = await Runner.run(decision_agent, decision_prompt)

    followup_question = decision_response.final_output.strip()
    return followup_question if followup_question.lower() != "null" else None


async def find_matching_schemes(query: str) -> Dict[str, Union[List[Dict[str, any]], str]]:
    matched_schemes = await query_schemes(query, top_k=10)

    matcher_agent = Agent(
        name="Scheme Recommendation Agent",
        instructions=SYSTEM_PROMPT,
        model=MODEL,
        tools=[]
    )

    matching_prompt = build_prompt(query, matched_schemes)
    match_response = await Runner.run(matcher_agent, matching_prompt)

    try:
        parsed_schemes = parse_matched_schemes(match_response.final_output)
        
        if len(parsed_schemes) > 10:
            followup_question = await get_followup_question(query, parsed_schemes)

            if followup_question:
                return {
                    "followup_needed": True,
                    "question": followup_question,
                    "top_matches": matched_schemes[:5]
                }

        return {"results": parsed_schemes}

    except Exception as e:
        raise ValueError(f"Failed to parse response: {str(e)}")


async def refine_results(original_query: str, followup_answer: str) -> List[Dict[str, any]]:
    combined_query = f"{original_query}. Additional context: {followup_answer}"
    result = await find_matching_schemes(combined_query)
    return result.get("results", [])
