import sys

from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
import uvicorn

from domain.user import user_router
from domain.admin import admin_router, admin_crud
from domain.board import board_router
from domain.chat import chat_router,chat_router_test

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router)
app.include_router(admin_router.router)
app.include_router(board_router.router)
app.include_router(chat_router.router)
app.include_router(chat_router_test.router)


if __name__ == "__main__":
    argv = sys.argv[1:]

    if len(argv) == 0:
        uvicorn.run("main:app", reload=True, log_level="debug")
    else:
        if "createsuperuser" in argv:
            admin_crud.create_admin_with_terminal()
