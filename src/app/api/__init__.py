"""API router exports."""

from fastapi import APIRouter

from .agent import router as agent_router

router = APIRouter()
router.include_router(agent_router, prefix="/agent", tags=["agent"])
