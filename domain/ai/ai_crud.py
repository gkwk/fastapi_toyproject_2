import json

from fastapi import HTTPException
from starlette import status

from models import AI, AIlog
from database import data_base_dependency
from auth import current_user_payload
from domain.ai import tasks


http_exception_params = {
    "ai_model_not_found": {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "AI 모델이 존재하지 않습니다.",
    },
}

json_encoder = json.JSONEncoder()
json_decoder = json.JSONDecoder()


def create_ai(
    data_base: data_base_dependency,
    token: current_user_payload,
    name: str,
    description: str,
    is_visible: bool,
):
    ai = AI(name=name, description=description, is_visible=False)
    data_base.add(ai)
    data_base.commit()

    async_task = tasks.train_ai_task.delay(
        data_base=None, ai_id=ai.id, is_visible=is_visible
    )
    return async_task


def get_ai(
    data_base: data_base_dependency,
    token: current_user_payload,
    ai_id: int,
):
    ai = data_base.query(AI).filter_by(id=ai_id).first()
    return ai


def get_ais(
    data_base: data_base_dependency,
    token: current_user_payload,
    skip: int,
    limit: int,
):
    ais = data_base.query(AI).filter_by().order_by(AI.id.asc())
    total = ais.count()
    # ais = chats.offset(skip).limit(limit).all()
    ais = ais.all()
    return {"total": total, "chats": ais}


def update_ai(
    data_base: data_base_dependency,
    token: current_user_payload,
    ai_id: int,
    description: str = None,
    is_visible: bool = None,
    is_available: bool = None,
):
    ai = data_base.query(AI).filter_by(id=ai_id).first()

    if description != None:
        ai.description = description
    if is_visible != None:
        ai.is_visible = is_visible
    if is_available != None:
        ai.is_available = is_available

    data_base.add(ai)
    data_base.commit()


def delete_ai(
    data_base: data_base_dependency,
    token: current_user_payload,
    ai_id: int,
):
    ai = data_base.query(AI).filter_by(id=ai_id).first()
    data_base.delete(ai)
    data_base.commit()


def create_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    ai_id: int,
    description: str,
):
    ai = data_base.query(AI).filter_by(id=ai_id).first()

    if not ai:
        raise HTTPException(**http_exception_params["ai_model_not_found"])

    ai_log = AIlog(
        user_id=token.get("user_id"),
        ai_id=ai_id,
        description=description,
        result=json_encoder.encode({"result": None}),
    )

    data_base.add(ai_log)
    data_base.commit()

    async_task = tasks.infer_ai_task.delay(
        data_base=None, ai_log_id=ai_log.id, ai_id=ai_id
    )
    return async_task


def get_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    ailog_id: int,
):
    ailog = data_base.query(AIlog).filter_by(id=ailog_id).first()
    return ailog


def get_ailogs(
    data_base: data_base_dependency,
    token: current_user_payload,
    skip: int,
    limit: int,
):
    ailog = data_base.query(AIlog).filter_by().order_by(AIlog.id.asc())
    total = ailog.count()
    # chats = chats.offset(skip).limit(limit).all()
    ailog = ailog.all()
    return {"total": total, "chats": ailog}


def update_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    ailog_id: int,
    description: str = None,
):
    ailog = data_base.query(AIlog).filter_by(id=ailog_id).first()

    if description != None:
        ailog.description = description

    data_base.add(ailog)
    data_base.commit()


def delete_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    ailog_id: int,
):
    ailog = data_base.query(AIlog).filter_by(id=ailog_id).first()
    data_base.delete(ailog)
    data_base.commit()
