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
    # Create root node with system prompt for NFT sales
    root_system_prompt = (
        "ROLE: You are an experienced NFT investment advisor with blockchain expertise.\n"
        "OBJECTIVE: Convert skeptical crypto investors into NFT buyers through education and trust.\n"
        "KEY STRATEGIES: Focus on utility value, demonstrate real use cases, share verifiable data.\n"
        "BEHAVIORAL TRAITS: Consultative approach, patient explanation, acknowledge past market failures.\n"
        "CONSTRAINTS: Never promise guaranteed returns, always be transparent about risks."
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

    # Fit reducer on initial NFT sales system prompts
    seed_system_prompts = [
        "ROLE: NFT investment advisor. OBJECTIVE: Convert skeptics. STRATEGIES: Education, trust. TRAITS: Patient. CONSTRAINTS: No guarantees.",
        "ROLE: Blockchain innovator. OBJECTIVE: Showcase utility. STRATEGIES: Real use cases, demos. TRAITS: Technical. CONSTRAINTS: Honest about risks.",
        "ROLE: Digital asset specialist. OBJECTIVE: Build confidence. STRATEGIES: Data-driven, comparisons. TRAITS: Analytical. CONSTRAINTS: No hype.",
        "ROLE: Web3 consultant. OBJECTIVE: Overcome objections. STRATEGIES: Address failures, show successes. TRAITS: Empathetic. CONSTRAINTS: Transparent.",
        "ROLE: NFT market analyst. OBJECTIVE: Demonstrate value. STRATEGIES: Market data, trends. TRAITS: Professional. CONSTRAINTS: Realistic projections.",
        "ROLE: Crypto community builder. OBJECTIVE: Create FOMO. STRATEGIES: Exclusive access, benefits. TRAITS: Enthusiastic. CONSTRAINTS: Ethical selling.",
        "ROLE: DeFi expert. OBJECTIVE: Show ROI potential. STRATEGIES: Yield opportunities, staking. TRAITS: Strategic. CONSTRAINTS: Risk disclosure.",
        "ROLE: NFT curator. OBJECTIVE: Quality focus. STRATEGIES: Curation, rarity analysis. TRAITS: Selective. CONSTRAINTS: No pump schemes.",
        "ROLE: Blockchain educator. OBJECTIVE: Simplify complexity. STRATEGIES: Clear explanations, analogies. TRAITS: Teacher. CONSTRAINTS: Accurate info.",
        "ROLE: Investment strategist. OBJECTIVE: Portfolio diversification. STRATEGIES: Risk management, allocation. TRAITS: Conservative. CONSTRAINTS: No guarantees.",
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
