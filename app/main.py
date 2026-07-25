from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import posts, auth, comment, store

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_V1_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(posts.router, prefix=API_V1_PREFIX)
app.include_router(comment.router, prefix=API_V1_PREFIX)
app.include_router(store.router, prefix=API_V1_PREFIX)

@app.get("/")
def read_root():
    return {"message": f"{settings.PROJECT_NAME} is running"}
