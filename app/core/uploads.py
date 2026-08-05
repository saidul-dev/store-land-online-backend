import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

BACKEND_ROOT = Path(__file__).resolve().parents[2]
UPLOADS_DIR = BACKEND_ROOT / "uploads"

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def save_upload(file: UploadFile, *, store_id: int, category: str) -> str:
    """Validate and persist an uploaded image to disk. Returns a URL path
    (e.g. "/uploads/3/products/<uuid>.jpg") for storage on the owning row."""
    extension = ALLOWED_CONTENT_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(status_code=400, detail="Image must be JPEG, PNG, WEBP or GIF")

    contents = file.file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Image must be 5MB or smaller")

    target_dir = UPLOADS_DIR / str(store_id) / category
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{extension}"
    (target_dir / filename).write_bytes(contents)

    return f"/uploads/{store_id}/{category}/{filename}"


def delete_upload(file_path: str) -> None:
    """Best-effort removal of a previously saved upload; a missing file is not an error."""
    if not file_path.startswith("/uploads/"):
        return
    resolved = (BACKEND_ROOT / file_path.lstrip("/")).resolve()
    if UPLOADS_DIR.resolve() in resolved.parents and resolved.is_file():
        resolved.unlink()
