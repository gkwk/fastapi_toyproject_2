import sys
import contextlib

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from starlette.middleware.cors import CORSMiddleware
import uvicorn

import v1_router
from domain.admin import admin_crud
from database import database_engine_shutdown


@contextlib.asynccontextmanager
async def app_lifespan(app: FastAPI):
    print("lifespan_start")
    yield
    print("lifespan_shutdown")
    database_engine_shutdown()


app = FastAPI(
    lifespan=app_lifespan,
    servers=[
        # {"url": "/test", "description": "Test environment"},
        # {"url": "/", "description": "Production environment"},
    ],
)

app.mount("/static", StaticFiles(directory="staticfile"), name="static")

# origins = ["http://localhost:3000", "http://127.0.0.1:3000"] # 프론트엔드가 사용하는 주소 추가
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router.router)


@app.get("/", tags=["main"])
def index_page(request: Request):
    print(request.cookies)
    return {"message": "Hello, FastAPI!"}


if __name__ == "__main__":
    argv = sys.argv[1:]

    if len(argv) == 0:
        uvicorn.run("main:app", reload=True, log_level="debug")
    else:
        if "createsuperuser" in argv:
            admin_crud.create_admin_with_terminal(data_base=None)
