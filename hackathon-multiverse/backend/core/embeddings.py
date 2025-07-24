import numpy as np
from typing import List, Tuple
from backend.core.logger import get_logger

logger = get_logger(__name__)


def embed(text: str) -> List[float]:
    """Stub embedding function - generates deterministic fake vector."""
    # Use hash to generate deterministic fake embedding
    h = hash(text)
    vec = []
    for i in range(5):
        # Generate 5 values between 0 and 1
        vec.append((h % (1000 * (i + 1))) / 1000.0)
    return vec


def fit_reducer(prompts: List[str]) -> None:
    """No-op for now - will implement real UMAP in Phase 4."""
    # TODO Phase-4: swap stub to real UMAP once UI wired
    logger.info(f"Stub fit_reducer called with {len(prompts)} prompts")
    pass


def to_xy(vec: List[float]) -> Tuple[float, float]:
    """Simple stub projection - just returns first two dimensions."""
    # TODO Phase-4: use fitted UMAP reducer for real projection
    if len(vec) >= 2:
        return (vec[0], vec[1])
    else:
        return (vec[0], 0.0) if vec else (0.0, 0.0)
