from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.uploads import UPLOADS_DIR
from app.api import posts, auth, comment, store, staff, product, order, category, brand, analytics, admin, plan, site_content

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

API_V1_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(posts.router, prefix=API_V1_PREFIX)
app.include_router(comment.router, prefix=API_V1_PREFIX)
app.include_router(store.router, prefix=API_V1_PREFIX)
app.include_router(staff.router, prefix=API_V1_PREFIX)
app.include_router(product.router, prefix=API_V1_PREFIX)
app.include_router(order.router, prefix=API_V1_PREFIX)
app.include_router(category.router, prefix=API_V1_PREFIX)
app.include_router(brand.router, prefix=API_V1_PREFIX)
app.include_router(analytics.router, prefix=API_V1_PREFIX)
app.include_router(admin.router, prefix=API_V1_PREFIX)
app.include_router(plan.router, prefix=API_V1_PREFIX)
app.include_router(site_content.router, prefix=API_V1_PREFIX)

@app.get("/")
def read_root():
    return {"message": f"{settings.PROJECT_NAME} is running"}
