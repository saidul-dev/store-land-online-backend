from fastapi import FastAPI
from app.core.config import settings
from app.api import posts

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(posts.router)


@app.get("/")
def read_root():
    return {"message": f"{settings.PROJECT_NAME} is running"}
