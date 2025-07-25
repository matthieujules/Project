from typing import List, Dict
from backend.llm.openai_client import chat, PolicyError
from backend.core.logger import get_logger
from backend.config.settings import settings
from backend.core.conversation import format_conversation_for_display

logger = get_logger(__name__)


async def variants(conversation_history: List[Dict[str, str]], k: int) -> List[str]:
    """Generate k strategic variations based on full conversation context.
    
    Returns: list_of_variants
    """
    try:
        # Handle empty conversation (root node case)
        if not conversation_history:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a strategic conversation designer. Generate initial prompts "
                        "that could start a dialogue with Putin about peace and conflict resolution. "
                        "Focus on approaches that might engage him constructively rather than defensively."
                    )
                },
                {
                    "role": "user",
                    "content": "Generate a thoughtful opening message to begin a dialogue with Putin about peace:"
                }
            ]
        else:
            # Format conversation for LLM
            conversation_text = format_conversation_for_display(conversation_history)
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a strategic conversation designer. Given this dialogue with Putin, "
                        "generate the next user message that will move him closer to accepting peace negotiations. "
                        "Build on what he just said - if he shows openness, exploit it. If he shows resistance, address it strategically. "
                        "Focus on finding common ground and incremental progress toward reconciliation."
                    )
                },
                {
                    "role": "user",
                    "content": f"Current conversation:\n\n{conversation_text}\n\nGenerate the next strategic message to move Putin toward reconciliation:"
                }
            ]
        
        # Use n parameter to get k variations in one call
        replies, _ = await chat(
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
        
        return variant_list
        
    except PolicyError as e:
        logger.warning(f"Policy violation in mutator: {e}")
        raise  # Bubble up as per spec
    except Exception as e:
        logger.error(f"Mutator error: {e}")
        raise
