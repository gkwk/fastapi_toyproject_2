import json

from celery_app import celery

from fastapi import APIRouter, HTTPException
from starlette import status

from models import AI, AIlog
from database import data_base_dependency
from domain.ai import ai_crud, ai_schema
from auth import current_user_payload
from database import get_data_base_decorator


router = APIRouter(
    prefix="/ai",
)

http_exception_params = {
    "ai_model_not_found": {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "AI 모델이 존재하지 않습니다.",
    },
}


json_encoder = json.JSONEncoder()


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


@router.post("/ai_infer", status_code=status.HTTP_201_CREATED)
def train_ai(
    data_base: data_base_dependency,
    token: current_user_payload,
    ai_id: int,
    information: str,
):
    ai = data_base.query(AI).filter_by(id=ai_id).first()

    if not ai:
        raise HTTPException(**http_exception_params["ai_model_not_found"])

    ai_log = AIlog(
        user_id=token.get("user_id"),
        ai_id=ai_id,
        information=information,
        result=json_encoder.encode({"result": None}),
    )

    data_base.add(ai_log)
    data_base.commit()

    async_task = celery.infer_ai_task.delay(data_base=None, ai_log_id=ai_log.id, ai_id=ai_id)
    return {"task_id": async_task.id}
