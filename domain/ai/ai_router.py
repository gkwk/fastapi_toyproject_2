from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from database import data_base_dependency
from domain.ai import ai_crud, ai_schema
from auth import current_user_payload, current_admin_payload


router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/train_ai", status_code=status.HTTP_201_CREATED)
def train_ai(
    data_base: data_base_dependency,
    token: current_admin_payload,
    schema: ai_schema.RequestAICreate,
):
    async_task = ai_crud.create_ai(
        data_base=data_base,
        token=token,
        name=schema.name,
        description=schema.description,
        is_visible=schema.is_visible,
    )

    return {"task_id": async_task.id}


@router.get("/get_ai")
def get_ai(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: Annotated[ai_schema.RequestAIRead, Depends()],
):
    return ai_crud.get_ai(
        data_base=data_base,
        token=token,
        ai_id=schema.ai_id,
    )


@router.get("/get_ais")
def get_ais(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: Annotated[ai_schema.RequestAIsRead, Depends()],
):
    return ai_crud.get_ais(
        data_base=data_base,
        token=token,
        is_available=schema.is_available,
        is_visible=schema.is_visible,
        skip=schema.skip,
        limit=schema.limit,
    )


@router.put("/update_ai", status_code=status.HTTP_204_NO_CONTENT)
def update_ai(
    data_base: data_base_dependency,
    token: current_admin_payload,
    schema: ai_schema.RequestAIUpdate,
):
    ai_crud.update_ai(
        data_base=data_base,
        token=token,
        ai_id=schema.ai_id,
        description=schema.description,
        is_visible=schema.is_visible,
        is_available=schema.is_available,
    )


@router.delete("/delete_ai", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai(
    data_base: data_base_dependency,
    token: current_admin_payload,
    schema: Annotated[ai_schema.RequestAIDelete, Depends()],
):
    ai_crud.delete_ai(
        data_base=data_base,
        token=token,
        ai_id=schema.ai_id,
    )


@router.post("/ai_infer", status_code=status.HTTP_201_CREATED)
def ai_infer(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: ai_schema.RequestAILogCreate,
):
    async_task = ai_crud.create_ailog(
        data_base=data_base,
        token=token,
        ai_id=schema.ai_id,
        description=schema.description,
    )
    return {"task_id": async_task.id}


@router.get("/get_ailog")
def get_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: Annotated[ai_schema.RequestAILogRead, Depends()],
):
    return ai_crud.get_ailog(
        data_base=data_base,
        token=token,
        ailog_id=schema.ailog_id,
    )


@router.get("/get_ailogs")
def get_ailogs(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: Annotated[ai_schema.RequestAILogsRead, Depends()],
):
    return ai_crud.get_ailogs(
        data_base=data_base,
        token=token,
        user_id=schema.user_id,
        ai_id=schema.ai_id,
        skip=schema.skip,
        limit=schema.limit,
    )


@router.put("/update_ailog", status_code=status.HTTP_204_NO_CONTENT)
def update_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: ai_schema.RequestAILogUpdate,
):
    ai_crud.update_ailog(
        data_base=data_base,
        token=token,
        ailog_id=schema.ailog_id,
        description=schema.description,
    )


@router.delete("/delete_ailog", status_code=status.HTTP_204_NO_CONTENT)
def delete_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: Annotated[ai_schema.RequestAILogDelete, Depends()],
):
    ai_crud.delete_ailog(
        data_base=data_base,
        token=token,
        ailog_id=schema.ailog_id,
    )
