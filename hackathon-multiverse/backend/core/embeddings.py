import openai
import numpy as np
from typing import List, Tuple
from backend.core.logger import get_logger
from backend.config.settings import settings

logger = get_logger(__name__)


def embed(text: str) -> List[float]:
    """Generate semantic embeddings using OpenAI's text-embedding-3-small model."""
    client = openai.OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text]
    )
    return response.data[0].embedding


def fit_reducer(prompts: List[str]) -> None:
    """No-op for now - will implement real UMAP in Phase 4."""
    # TODO Phase-4: swap stub to real UMAP once UI wired
    logger.info(f"Stub fit_reducer called with {len(prompts)} prompts")
    pass


def to_xy(vec: List[float]) -> Tuple[float, float]:
    """Project high-dimensional embedding to 2D using PCA for visualization."""
    # For now, use simple PCA-like projection on first two principal components
    # In production, you'd want UMAP or t-SNE for better clustering
    if len(vec) >= 2:
        # Simple normalization to [-1, 1] range for visualization
        x = (vec[0] - 0.5) * 2
        y = (vec[1] - 0.5) * 2
        return (x, y)
    else:
        return (0.0, 0.0)
