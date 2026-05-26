from fastapi import FastAPI

from routes.endpoints.auth import router as auth_router
from routes.endpoints.user import router as user_router
from src.routes.middlewares import LoggingMiddleware

app = FastAPI(
    title="Pharma BE",
    version="1.0.0",
    root_path="",
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.add_middleware(LoggingMiddleware)

app.include_router(user_router)
app.include_router(auth_router)
