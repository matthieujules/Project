from fastapi import APIRouter, HTTPException
from backend.core.schemas import FocusZone, SettingsUpdate
from backend.orchestrator.scheduler import boost_or_seed
from backend.config.settings import settings
from backend.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/focus_zone")
async def focus_zone(payload: FocusZone):
    """
    Handle focus zone requests - either boost existing nodes or seed new ones.
    """
    try:
        result = await boost_or_seed(payload)
        return result
    except Exception as e:
        logger.error(f"Error processing focus zone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/settings")
async def update_settings(updates: SettingsUpdate):
    """
    Update lambda values at runtime.
    """
    try:
        # Update only provided values
        if updates.lambda_trend is not None:
            settings.lambda_trend = updates.lambda_trend
        if updates.lambda_sim is not None:
            settings.lambda_sim = updates.lambda_sim
        if updates.lambda_depth is not None:
            settings.lambda_depth = updates.lambda_depth

        # Return full settings
        return {
            "lambda_trend": settings.lambda_trend,
            "lambda_sim": settings.lambda_sim,
            "lambda_depth": settings.lambda_depth,
            "redis_url": settings.redis_url,
            "log_level": settings.log_level,
        }
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings")
async def get_settings():
    """
    Get current settings.
    """
    return {
        "lambda_trend": settings.lambda_trend,
        "lambda_sim": settings.lambda_sim,
        "lambda_depth": settings.lambda_depth,
        "redis_url": settings.redis_url,
        "log_level": settings.log_level,
    }
