from fastapi import APIRouter

from domain.user import user_router
from domain.admin import admin_router
from domain.board import board_router
from domain.chat import chat_router, chat_router_test
from domain.ai import ai_router

from domain import ai

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(user_router.router)
router.include_router(admin_router.router)
router.include_router(board_router.router)
router.include_router(chat_router.router)
router.include_router(chat_router_test.router)
router.include_router(ai_router.router)
