from fastapi import APIRouter

from .monitoring import router as monitor_router
from .warframe import router as warframe_router

api_router = APIRouter(prefix="/api")

api_router.include_router(warframe_router)
api_router.include_router(monitor_router)
