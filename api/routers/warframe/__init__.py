from fastapi import APIRouter

from .items import router as items_router
from .tracking import router as order_tracking_router

router = APIRouter(prefix="/warframe")

router.include_router(items_router, prefix="/items")
router.include_router(order_tracking_router, prefix="/track")

__all__ = ("router",)
