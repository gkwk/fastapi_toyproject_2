from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
import uvicorn

from domain.user import user_router

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


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level="debug")
