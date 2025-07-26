#!/usr/bin/env python3
"""Push initial seed node to Redis frontier and fit UMAP reducer."""

import sys
import os
# Add parent directory to path so backend module can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.schemas import Node
from backend.core.utils import uuid_str
from backend.db.node_store import save
from backend.db.frontier import push
from backend.core.logger import get_logger
from backend.core.embeddings import fit_reducer, embed, to_xy

logger = get_logger(__name__)


def main():
    """Create and push root system prompt node, then fit reducer."""
    # Create root node with system prompt
    root_system_prompt = (
        "You are a skilled diplomatic negotiator. Your goal is to guide Putin toward "
        "accepting peace negotiations through empathetic understanding and finding common ground. "
        "Acknowledge his concerns, build trust gradually, and focus on mutual benefits."
    )
    emb = embed(root_system_prompt)

    root = Node(
        id=uuid_str(),
        system_prompt=root_system_prompt,
        conversation_samples=[],
        depth=0,
        score=0.5,
        avg_score=0.5,
        sample_count=0,
        emb=emb,
        xy=[0.0, 0.0],  # Will be updated after fitting reducer
    )

    # Save node and push to frontier
    save(root)
    push(root.id, 1.0)

    logger.info(f"Seeded root node {root.id} with system prompt: {root_system_prompt[:60]}...")
    print(f"Root system prompt node created: {root.id}")

    # Fit reducer on initial system prompts
    seed_system_prompts = [
        "You are a diplomatic negotiator focused on finding common ground through empathy.",
        "You are an economic strategist emphasizing mutual trade benefits.",
        "You are a security expert addressing legitimate concerns while building trust.",
        "You are a collaborative problem-solver seeking win-win solutions.",
        "You are a historian using past peace precedents to guide negotiations.",
        "You are a mediator skilled in de-escalation and conflict resolution.",
        "You are a cultural bridge-builder focusing on shared values.",
        "You are a pragmatic diplomat balancing firmness with respect.",
        "You are a peace architect designing step-by-step agreements.",
        "You are a strategic communicator adapting to Putin's responses.",
    ]

    fit_reducer(seed_system_prompts)
    logger.info("Fitted UMAP reducer on seed system prompts")

    # Update root node with proper 2D projection
    xy = list(to_xy(emb))
    root.xy = xy
    save(root)

    print(f"UMAP reducer fitted, root node projected to xy=({xy[0]:.2f}, {xy[1]:.2f})")


if __name__ == "__main__":
    main()
