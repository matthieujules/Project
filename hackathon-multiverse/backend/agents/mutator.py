from typing import List
from backend.llm.openai_client import chat, PolicyError
from backend.core.logger import get_logger
from backend.config.settings import settings

logger = get_logger(__name__)


async def variants(base_prompt: str, k: int) -> tuple[List[str], dict]:
    """Generate k variations of the prompt exploring different angles.
    
    Returns: (list_of_variants, usage_dict)
    """
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a creative prompt engineer. Given a prompt about peace or conflict, "
                    "generate ONE meaningful variation that explores a different perspective, "
                    "framing, or aspect while staying on topic."
                )
            },
            {
                "role": "user",
                "content": f"Create a variation of this prompt:\n\n{base_prompt}"
            }
        ]
        
        # Use n parameter to get k variations in one call
        replies, usage = await chat(
            model=settings.mutator_model,
            messages=messages,
            temperature=0.9,  # Higher temperature for more creativity
            n=k  # Get k different completions
        )
        
        # Ensure replies is a list (it should be when n > 1)
        if isinstance(replies, str):
            variant_list = [replies]
        else:
            variant_list = replies
        
        return variant_list, usage
        
    except PolicyError as e:
        logger.warning(f"Policy violation in mutator: {e}")
        raise  # Bubble up as per spec
    except Exception as e:
        logger.error(f"Mutator error: {e}")
        raise
