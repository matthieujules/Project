import asyncio
from typing import List, Dict
from backend.llm.openai_client import chat, PolicyError
from backend.core.logger import get_logger
from backend.config.settings import settings

logger = get_logger(__name__)


async def mutate_system_prompt(parent_prompt: str, performance_data: Dict, k: int) -> List[str]:
    """Generate k variations of system prompt based on performance feedback.
    
    Args:
        parent_prompt: The system prompt to mutate
        performance_data: Dict with avg_score, sample_count, etc.
        k: Number of variants to generate
    
    Returns: list of system prompt variants
    """
    try:
        # Handle initial system prompt (root node case)
        if not parent_prompt:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a meta-prompt engineer optimizing instructions for a diplomatic agent. "
                        "Generate initial system prompts that will guide an agent to have effective "
                        "conversations with Putin about peace negotiations. Focus on different "
                        "persuasion strategies and communication approaches.\n\n"
                        "CRITICAL: Output ONLY the exact system prompt text that should be given to "
                        "the diplomatic agent. Do not include explanations or meta-commentary."
                    )
                },
                {
                    "role": "user",
                    "content": "Generate an initial system prompt for a diplomatic agent to engage Putin in peace negotiations. Output only the system prompt text:"
                }
            ]
        else:
            # Format performance feedback
            performance_text = f"Average Score: {performance_data.get('avg_score', 0.0):.3f}, Conversations Tested: {performance_data.get('sample_count', 0)}"
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a meta-prompt engineer optimizing instructions for a diplomatic agent. "
                        "Given a system prompt and its performance data, generate improved variants that "
                        "might be more effective at achieving peace negotiations with Putin.\n\n"
                        "Focus on exploring different approaches:\n"
                        "- Persuasion strategies (empathy, logic, authority, shared interests)\n"
                        "- Communication styles (formal, collaborative, direct, incremental)\n"
                        "- Psychological approaches (acknowledge concerns, build trust, find common ground)\n"
                        "- Tactical variations (economic focus, security focus, legacy focus)\n\n"
                        "CRITICAL: Output ONLY the exact system prompt text that should be given to "
                        "the diplomatic agent. Do not include explanations, strategies, or meta-commentary."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Parent system prompt: '{parent_prompt}'\n"
                        f"Performance: {performance_text}\n\n"
                        "Generate an improved variant of this system prompt. "
                        "Output only the system prompt text, no explanations:"
                    )
                }
            ]
        
        # Generate multiple variants concurrently
        variant_tasks = []
        for i in range(k):
            variant_tasks.append(chat(
                model=settings.mutator_model,
                messages=messages,
                temperature=0.9  # High temperature for creativity in system prompt space
            ))
        
        # Execute all calls concurrently
        results = await asyncio.gather(*variant_tasks)
        variant_list = [reply for reply, _ in results]
        
        return variant_list
        
    except PolicyError as e:
        logger.warning(f"Policy violation in system prompt mutator: {e}")
        raise  # Bubble up as per spec
    except Exception as e:
        logger.error(f"System prompt mutator error: {e}")
        raise


async def generate_initial_system_prompts(k: int = 3) -> List[str]:
    """Generate initial system prompts for seeding the exploration."""
    
    base_prompts = [
        (
            "You are a skilled diplomatic negotiator. Your goal is to guide Putin toward "
            "accepting peace negotiations through empathetic understanding and finding common ground. "
            "Acknowledge his concerns, build trust gradually, and focus on mutual benefits. "
            "Be respectful, patient, and strategic in your approach."
        ),
        (
            "You are an economic strategist focused on practical solutions. Your goal is to "
            "convince Putin that peace negotiations serve Russia's economic interests. "
            "Emphasize trade opportunities, reduced military costs, and economic partnerships. "
            "Use concrete examples and focus on tangible benefits for Russia."
        ),
        (
            "You are a security-focused diplomat. Your goal is to address Putin's security "
            "concerns while moving toward peace negotiations. Acknowledge legitimate Russian "
            "security needs, propose specific security arrangements, and build confidence "
            "through step-by-step agreements."
        )
    ]
    
    # If k <= 3, return the base prompts
    if k <= len(base_prompts):
        return base_prompts[:k]
    
    # If k > 3, generate additional variants
    additional_needed = k - len(base_prompts)
    additional_prompts = await mutate_system_prompt("", {}, additional_needed)
    
    return base_prompts + additional_prompts