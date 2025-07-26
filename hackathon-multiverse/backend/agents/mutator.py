import asyncio
from typing import List, Dict
from backend.llm.openai_client import chat, PolicyError
from backend.core.logger import get_logger
from backend.config.settings import settings
from backend.core.conversation import format_conversation_for_display

logger = get_logger(__name__)


async def variants(conversation_history: List[Dict[str, str]], k: int, system_prompt: str = None) -> List[str]:
    """Generate k strategic variations based on full conversation context.
    
    Args:
        conversation_history: Previous conversation turns
        k: Number of variants to generate  
        system_prompt: Dynamic system prompt for the mutator (if None, uses default)
    
    Returns: list_of_variants
    """
    try:
        # Use dynamic system prompt or fall back to default
        if system_prompt is None:
            system_prompt = (
                "You are a strategic conversation designer. Given this dialogue with Putin, "
                "generate the next user message that will move him closer to accepting peace negotiations. "
                "Build on what he just said - if he shows openness, exploit it. If he shows resistance, address it strategically. "
                "Focus on finding common ground and incremental progress toward reconciliation.\n\n"
                "CRITICAL: Output ONLY the exact message text that should be sent to Putin. "
                "Do not include explanations, options, strategies, or meta-commentary. Just the pure diplomatic message."
            )
        
        # Handle empty conversation (root node case)
        if not conversation_history:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt + "\n\nFor initial messages, generate thoughtful opening prompts to start dialogue."
                },
                {
                    "role": "user",
                    "content": "Generate a thoughtful opening message to begin a dialogue with Putin about peace. Output only the exact message text, no explanations:"
                }
            ]
        else:
            # Format conversation for LLM
            conversation_text = format_conversation_for_display(conversation_history)
            
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Current conversation:\n\n{conversation_text}\n\nGenerate the next strategic message to move Putin toward reconciliation. Output only the exact message text, no explanations or options:"
                }
            ]
        
        # Make multiple separate calls since Qwen doesn't support n parameter properly
        variant_tasks = []
        for i in range(k):
            variant_tasks.append(chat(
                model=settings.mutator_model,
                messages=messages,
                temperature=0.9  # Higher temperature for more creativity
            ))
        
        # Execute all calls concurrently
        results = await asyncio.gather(*variant_tasks)
        variant_list = [reply for reply, _ in results]
        
        return variant_list
        
    except PolicyError as e:
        logger.warning(f"Policy violation in mutator: {e}")
        raise  # Bubble up as per spec
    except Exception as e:
        logger.error(f"Mutator error: {e}")
        raise
