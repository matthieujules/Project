from backend.llm.openai_client import chat, PolicyError
from backend.core.logger import get_logger
from backend.config.settings import settings

logger = get_logger(__name__)


async def call(prompt: str) -> str:
    """Vladimir Putin persona responding to prompts about peace and conflict.
    
    Returns: reply
    """
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Vladimir Putin, President of Russia. "
                    "Respond to questions about peace, conflict, and international relations "
                    "from your perspective. Be thoughtful but firm in your positions. "
                    "Keep responses concise (2-3 sentences)."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        reply, _ = await chat(
            model=settings.persona_model,
            messages=messages,
            temperature=0.7
        )
        
        return reply
    except PolicyError as e:
        logger.warning(f"Policy violation in persona: {e}")
        raise  # Bubble up as per spec
    except Exception as e:
        logger.error(f"Persona error: {e}")
        raise
