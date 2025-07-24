import asyncio
from backend.db.frontier import pop_max, push, size as frontier_size
from backend.db.node_store import get, save
from backend.db.redis_client import get_redis
from backend.agents.mutator import variants
from backend.agents.persona import call
from backend.agents.critic import score
from backend.core.schemas import Node, GraphUpdate
from backend.core.utils import uuid_str
from backend.core.logger import get_logger
from backend.core.embeddings import embed, to_xy
from backend.orchestrator.scheduler import calculate_priority, get_top_k_nodes
from backend.config.settings import settings
from backend.llm.openai_client import PolicyError

logger = get_logger(__name__)




async def log_worker_heartbeat():
    """Log worker status every 60 seconds."""
    r = get_redis()
    
    while True:
        await asyncio.sleep(60)
        
        # Get current stats
        total_cost = r.get("usage:total_cost")
        current_cost = float(total_cost) if total_cost else 0.0
        f_size = frontier_size()
        node_count = len(r.keys("node:*"))
        
        logger.info(
            f"Worker heartbeat - frontier_size={f_size}, total_nodes={node_count}, "
            f"total_cost=${current_cost:.2f}, budget_remaining=${settings.daily_budget_usd - current_cost:.2f}"
        )


async def process_one_node():
    """Process a single node from the frontier."""
    # Before each expansion, check budget
    r = get_redis()
    current_cost = float(r.get("usage:total_cost") or 0.0)
    if current_cost >= settings.daily_budget_usd:
        logger.warning("Budget exhausted – sleeping 60 s")
        await asyncio.sleep(60)
        return True  # Return True to indicate we processed something (slept)

    # Pop highest priority node
    parent_id = pop_max()
    if not parent_id:
        return False  # No nodes to process

    # Get parent node
    parent = get(parent_id)
    if not parent:
        logger.error(f"Parent node {parent_id} not found")
        return True

    logger.info(f"Processing node {parent_id} at depth {parent.depth}")

    # Get top K nodes for similarity calculation
    top_k_nodes = get_top_k_nodes(k=10)
    top_k_embeddings = [n.emb for n in top_k_nodes if n.emb]

    # Generate variants
    variant_list, mutator_usage = await variants(parent.prompt, k=3)
    
    # Process each variant
    for variant_prompt in variant_list:
        child_id = uuid_str()  # Generate ID early for logging
        
        try:
            # Call persona
            reply, persona_usage = await call(variant_prompt)

            # Get score from critic
            s, critic_usage = await score(variant_prompt, reply)
            
        except Exception as e:
            # Log error and skip this variant
            logger.error(f"Error processing variant: {e}")
            continue

        # Generate embedding and 2D projection
        emb = embed(variant_prompt)
        xy = list(to_xy(emb))  # Convert tuple to list for JSON serialization
        
        # Calculate total costs
        total_tokens_in = persona_usage['prompt_tokens'] + critic_usage['prompt_tokens']
        total_tokens_out = persona_usage['completion_tokens'] + critic_usage['completion_tokens']
        mut_cost_each = mutator_usage['cost'] / len(variant_list)
        total_cost = persona_usage['cost'] + critic_usage['cost'] + mut_cost_each
        
        # Log per-turn as specified
        logger.info(
            f"node={child_id} depth={parent.depth + 1} parent={parent.id} "
            f"tokens_in={total_tokens_in} tokens_out={total_tokens_out} "
            f"cost=${total_cost:.2f} personaCost=${persona_usage['cost']:.2f} "
            f"mutCost=${mut_cost_each:.2f} "
            f"criticCost=${critic_usage['cost']:.2f}"
        )

        # Create child node
        child = Node(
            id=child_id,  # Use the pre-generated ID
            prompt=variant_prompt,
            reply=reply,
            score=s,
            depth=parent.depth + 1,
            parent=parent.id,
            emb=emb,
            xy=xy,
            prompt_tokens=total_tokens_in,
            completion_tokens=total_tokens_out,
            agent_cost=total_cost,
        )

        # Calculate priority using scheduler
        priority = calculate_priority(
            child, parent_score=parent.score, top_k_embeddings=top_k_embeddings
        )

        # Save child and push to frontier with calculated priority
        save(child)
        push(child.id, priority)

        # Publish GraphUpdate to Redis for WebSocket broadcast
        graph_update = GraphUpdate(
            id=child.id, xy=child.xy, score=child.score, parent=child.parent
        )
        r = get_redis()
        r.publish("graph_updates", graph_update.model_dump_json())

        logger.info(
            f"Created child {child.id} with score {s:.3f}, "
            f"priority {priority:.3f}, xy=({xy[0]:.2f}, {xy[1]:.2f})"
        )

    return True


async def main():
    """Main worker loop."""
    logger.info("Worker starting...")
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(log_worker_heartbeat())

    try:
        while True:
            try:
                # Try to process a node
                processed = await process_one_node()

                if not processed:
                    # No nodes available, wait a bit
                    await asyncio.sleep(0.1)
                else:
                    # Small delay to prevent tight loop
                    await asyncio.sleep(0.01)

            except KeyboardInterrupt:
                logger.info("Worker shutting down...")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)
    finally:
        # Cancel heartbeat task
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
