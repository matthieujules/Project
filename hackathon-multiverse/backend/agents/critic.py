import json
from backend.llm.openai_client import chat, PolicyError
from backend.core.logger import get_logger
from backend.config.settings import settings

logger = get_logger(__name__)


async def score(prompt: str, reply: str) -> float:
    """Score the quality of a prompt-reply pair for peace/conflict dialogue.
    
    Returns: score
    """
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a dialogue quality critic. Score the following prompt-reply pair "
                    "based on: depth of insight, constructiveness, nuance, and potential to lead "
                    "to meaningful dialogue about peace and conflict."
                )
            },
            {
                "role": "user",
                "content": f"Prompt: {prompt}\n\nReply: {reply}"
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
