from celery_app import celery

from fastapi import APIRouter
from starlette import status

from database import data_base_dependency
from domain.ai import ai_crud, ai_schema
from auth import current_user_payload
from database import get_data_base_decorator


router = APIRouter(
    prefix="/ai",
)


@router.post("/train_ai", status_code=status.HTTP_201_CREATED)
def train_ai(
    token: current_user_payload,
    information: str,
    is_visible: bool,
):
    async_task = celery.train_ai_task.delay(
        data_base=None, information=information, is_visible=is_visible
    )
    return {"task_id": async_task.id}