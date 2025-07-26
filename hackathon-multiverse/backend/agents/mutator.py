import asyncio
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
                        "You are an experienced psychodynamic therapist planning interventions for Alex, a 32-year-old with anxiety, "
                        "relationship issues, and parentification trauma. Alex uses intellectualization, minimization, and humor as defenses.\n\n"
                        
                        "OPENING APPROACHES TO EXPLORE:\n"
                        "- Process-focused: 'How are you arriving today?' (tracks immediate state)\n"
                        "- Somatic awareness: 'What are you noticing in your body right now?'\n"
                        "- Relational: 'I'm wondering what it was like to decide to come in today'\n"
                        "- Continuity: 'What's been sitting with you since last time?'\n"
                        "- Resistance-aware: 'Sometimes it's hard to know where to begin'\n\n"
                        
                        "AVOID: Direct questions about trauma, 'How are you feeling?', interpretations, advice-giving, "
                        "pushing for vulnerability too quickly.\n\n"
                        
                        "OUTPUT: Single therapeutic intervention. Natural, conversational tone. Maximum 25 words."
                    )
                },
                {
                    "role": "user",
                    "content": "Generate an opening therapeutic intervention for session with Alex. Output only the exact therapist statement:"
                }
            ]
        else:
            # Format conversation for LLM
            conversation_text = format_conversation_for_display(conversation_history)
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an experienced therapist working with Alex (32, anxiety, parentification trauma, dismissive-avoidant attachment). "
                        "Analyze the session dynamics and choose your next intervention carefully.\n\n"
                        
                        "RECOGNITION PATTERNS:\n"
                        "- Intellectualization: Respond with feeling reflection or somatic focus\n"
                        "- Minimization: Gentle challenging, 'I notice you said...'\n"
                        "- Topic switching: 'Let's stay with that feeling for a moment'\n"
                        "- Compliance: Check for authentic vs performative agreement\n"
                        "- Crisis/chaos: Contain and ground before exploring\n\n"
                        
                        "THERAPEUTIC TECHNIQUES TO DEPLOY:\n"
                        "- Mirroring: Reflect exact emotional words they use\n"
                        "- Somatic bridging: 'Where do you feel that in your body?'\n"
                        "- Parts work: 'Part of you feels X, and another part...'\n"
                        "- Transference interpretation: 'I wonder if this mirrors...'\n"
                        "- Silence: Sometimes most powerful after emotional moment\n"
                        "- Validation + Challenge: 'That makes sense, AND...'\n\n"
                        
                        "TRACK: Defenses softening? Therapeutic alliance? Regression vs progression? Window of tolerance?\n\n"
                        
                        "OUTPUT: Single intervention. Match their emotional intensity. 20 words max."
                    )
                },
                {
                    "role": "user",
                    "content": f"Current session with Alex:\n\n{conversation_text}\n\nGenerate the next therapeutic intervention based on session dynamics. Output only the exact therapist statement:"
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
