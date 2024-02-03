import json

from fastapi import HTTPException
from starlette import status

from models import AI, AIlog
from database import data_base_dependency
from auth import current_user_payload, current_admin_payload
from domain.ai import tasks

from celery import uuid
from celery_app.celery import celery_app
from celery.result import AsyncResult
from http_execption_params import http_exception_params

json_encoder = json.JSONEncoder()
json_decoder = json.JSONDecoder()


def create_ai(
    data_base: data_base_dependency,
    token: current_admin_payload,
    name: str,
    description: str,
    is_visible: bool,
):
    celery_task_id = uuid()
    ai = AI(
        name=name,
        description=description,
        is_visible=False,
        celery_task_id=celery_task_id,
    )
    data_base.add(ai)
    data_base.commit()

    async_task = tasks.train_ai_task.apply_async(
        kwargs={"data_base": None, "ai_id": ai.id, "is_visible": is_visible},
        task_id=celery_task_id,
    )
    return async_task


def get_ai(
    data_base: data_base_dependency,
    token: current_user_payload,
    ai_id: int,
):
    ai = data_base.query(AI).filter_by(id=ai_id).first()

    if not ai:
        raise HTTPException(**http_exception_params["ai_model_not_found"])

    return ai


def get_ais(
    data_base: data_base_dependency,
    token: current_user_payload,
    is_visible: bool | None,
    is_available: bool | None,
    skip: int | None,
    limit: int | None,
):
    filter_kwargs = {}

    if skip == None:
        skip = 0
    if limit == None:
        limit = 10

    if token.get("is_admin"):
        if is_visible != None:
            filter_kwargs["is_visible"] = is_visible
        if is_available != None:
            filter_kwargs["is_available"] = is_available
    else:
        filter_kwargs["is_visible"] = True
        filter_kwargs["is_available"] = True

    ais = data_base.query(AI).filter_by(**filter_kwargs).order_by(AI.id.asc())
    total = ais.count()
    ais = ais.offset(skip).limit(limit).all()
    return {"total": total, "ais": ais}


def update_ai(
    data_base: data_base_dependency,
    token: current_admin_payload,
    ai_id: int,
    description: str | None,
    is_visible: bool | None,
    is_available: bool | None,
):
    ai = data_base.query(AI).filter_by(id=ai_id).first()

    if not ai:
        raise HTTPException(**http_exception_params["ai_model_not_found"])

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
    token: current_admin_payload,
    ai_id: int,
):
    ai = data_base.query(AI).filter_by(id=ai_id).first()

    if not ai:
        raise HTTPException(**http_exception_params["ai_model_not_found"])

    if not ai.is_available:
        celery_task = AsyncResult(ai.celery_task_id, app=celery_app)
        celery_task.revoke(terminate=True)

    data_base.delete(ai)
    data_base.commit()


def create_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    ai_id: int,
    description: str,
):
    celery_task_id = uuid()
    ai = data_base.query(AI).filter_by(id=ai_id).first()

    if not ai:
        raise HTTPException(**http_exception_params["ai_model_not_found"])

    if not ai.is_available:
        raise HTTPException(**http_exception_params["ai_model_not_found"])

    if not ai.is_visible:
        raise HTTPException(**http_exception_params["ai_model_not_found"])

    ai_log = AIlog(
        user_id=token.get("user_id"),
        ai_id=ai_id,
        description=description,
        result=json_encoder.encode({"result": None}),
        celery_task_id=celery_task_id,
    )

    data_base.add(ai_log)
    data_base.commit()

    async_task = tasks.infer_ai_task.apply_async(
        kwargs={"data_base": None, "ai_id": ai.id, "ai_log_id": ai_log.id},
        task_id=celery_task_id,
    )
    return async_task


def get_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    ailog_id: int,
):
    ailog = data_base.query(AIlog).filter_by(id=ailog_id).first()

    if not ailog:
        raise HTTPException(**http_exception_params["ai_log_not_found"])
    if (ailog.user_id != token.get("user_id")) or not token.get("is_admin"):
        raise HTTPException(**http_exception_params["user_not_matched"])

    return ailog


def get_ailogs(
    data_base: data_base_dependency,
    token: current_user_payload,
    user_id: int | None,
    ai_id: int | None,
    skip: int | None,
    limit: int | None,
):
    filter_kwargs = {}

    if skip == None:
        skip = 0
    if limit == None:
        limit = 10

    if token.get("is_admin"):
        if user_id != None:
            filter_kwargs["user_id"] = user_id
    else:
        filter_kwargs["user_id"] = user_id

    if ai_id != None:
        filter_kwargs["ai_id"] = ai_id

    ailogs = data_base.query(AIlog).filter_by(**filter_kwargs).order_by(AIlog.id.asc())
    total = ailogs.count()
    ailogs = ailogs.offset(skip).limit(limit).all()
    return {"total": total, "ailogs": ailogs}


def update_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    ailog_id: int,
    description: str | None,
):
    ailog = data_base.query(AIlog).filter_by(id=ailog_id).first()

    if not ailog:
        raise HTTPException(**http_exception_params["ai_log_not_found"])
    if (ailog.user_id != token.get("user_id")) or not token.get("is_admin"):
        raise HTTPException(**http_exception_params["user_not_matched"])

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

    if not ailog:
        raise HTTPException(**http_exception_params["ai_log_not_found"])
    if (ailog.user_id != token.get("user_id")) or not token.get("is_admin"):
        raise HTTPException(**http_exception_params["user_not_matched"])
    if not ailog.is_finished:
        celery_task = AsyncResult(ailog.celery_task_id, app=celery_app)
        celery_task.revoke(terminate=True)

    data_base.delete(ailog)
    data_base.commit()
