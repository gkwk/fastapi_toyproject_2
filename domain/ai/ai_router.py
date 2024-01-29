from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from database import data_base_dependency
from domain.ai import ai_crud, ai_schema
from auth import current_user_payload


router = APIRouter(
    prefix="/ai",
)

http_exception_params = {
    "ai_model_not_found": {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "AI 모델이 존재하지 않습니다.",
    },
}


@router.post("/train_ai", status_code=status.HTTP_201_CREATED)
def train_ai(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: ai_schema.AICreate,
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
    schema: ai_schema.AIRead = Depends(),
):
    return ai_crud.get_ai(data_base=data_base, token=token, ai_id=schema.ai_id)


@router.get("/get_ais")
def get_ais(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: ai_schema.AIsRead = Depends(),
):
    return ai_crud.get_ais(
        data_base=data_base, token=token, skip=schema.skip, limit=schema.limit
    )


@router.put("/update_ai", status_code=status.HTTP_204_NO_CONTENT)
def update_ai(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: ai_schema.AIUpdate,
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
    token: current_user_payload,
    schema: ai_schema.AIDelete,
):
    ai_crud.delete_ai(data_base=data_base, token=token, ai_id=schema.ai_id)


@router.post("/ai_infer", status_code=status.HTTP_201_CREATED)
def ai_infer(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: ai_schema.AILogCreate,
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
    schema: ai_schema.AILogRead = Depends(),
):
    return ai_crud.get_ailog(data_base=data_base, token=token, ailog_id=schema.ailog_id)


@router.get("/get_ailogs")
def get_ailogs(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: ai_schema.AILogsRead = Depends(),
):
    return ai_crud.get_ailogs(
        data_base=data_base, token=token, skip=schema.skip, limit=schema.limit
    )


@router.put("/update_ailog", status_code=status.HTTP_204_NO_CONTENT)
def update_ailog(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: ai_schema.AILogUpdate,
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
    schema: ai_schema.AILogDelete,
):
    ai_crud.delete_ailog(data_base=data_base, token=token, ailog_id=schema.ailog_id)
