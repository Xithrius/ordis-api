from fastapi import APIRouter

from .items import router as items_router

router = APIRouter(prefix="/warframe")

router.include_router(items_router, prefix="/items")

__all__ = ("router",)
