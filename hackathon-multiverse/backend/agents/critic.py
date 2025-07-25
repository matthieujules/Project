import json
from typing import List, Dict
from backend.llm.openai_client import chat, PolicyError
from backend.core.logger import get_logger
from backend.config.settings import settings
from backend.core.conversation import format_conversation_for_display

logger = get_logger(__name__)


async def score(conversation_history: List[Dict[str, str]]) -> float:
    """Score the entire conversation trajectory toward reconciliation goal.
    
    Returns: score
    """
    try:
        # Format conversation for LLM
        conversation_text = format_conversation_for_display(conversation_history)
        
        # Handle initial exchanges vs multi-turn conversations
        if len(conversation_history) <= 2:
            system_content = (
                "You are a negotiation progress evaluator. Score this initial exchange with Putin "
                "based on how receptive or hostile his response is to peace dialogue. "
                "Look for: openness to discussion, defensive reactions, constructive engagement, or outright hostility. "
                "Rate 0.0 (completely hostile) to 1.0 (very receptive to peace talks)."
            )
            user_content = f"Initial exchange to evaluate:\n\n{conversation_text}\n\nScore Putin's receptiveness to peace dialogue:"
        else:
            system_content = (
                "You are a negotiation progress evaluator. Score this ENTIRE conversation "
                "based on how much Putin has moved from initial hostility toward accepting "
                "peace negotiations. Look for: softening of positions, acknowledgment of common ground, "
                "willingness to engage constructively, and openness to compromise. "
                "Rate 0.0 (hostile/regressive) to 1.0 (ready for peace talks)."
            )
            user_content = f"Full conversation to evaluate:\n\n{conversation_text}\n\nScore Putin's trajectory toward reconciliation:"
        
        messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]
        
        # Use function calling for structured output
        tools = [{
            "type": "function",
            "function": {
                "name": "score_dialogue",
                "description": "Score a dialogue exchange",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Quality score from 0.0 (poor) to 1.0 (excellent)"
                        },
                        "rationale": {
                            "type": "string",
                            "description": "Brief explanation of the score"
                        }
                    },
                    "required": ["score", "rationale"]
                }
            }
        }]
        
        reply_json, _ = await chat(
            model=settings.critic_model,
            messages=messages,
            temperature=0.0,  # Deterministic scoring
            tools=tools
        )
        
        # Parse the JSON response
        result = json.loads(reply_json)
        score_value = float(result["score"])
        
        return score_value
        
    except PolicyError as e:
        logger.warning(f"Policy violation in critic: {e}")
        raise  # Bubble up as per spec
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Failed to parse critic response: {e}")
        raise
    except Exception as e:
        logger.error(f"Critic error: {e}")
        raise
