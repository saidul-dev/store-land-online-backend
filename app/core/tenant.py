from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.store import store as store_crud
from app.db.session import get_db
from app.models.store import Store


def extract_subdomain(host: str) -> str | None:
    """Return the subdomain label if host is "<label>.<BASE_DOMAIN>", else None."""
    bare_host = host.split(":")[0].lower()
    base = settings.BASE_DOMAIN.lower()

    if bare_host in (base, f"www.{base}"):
        return None
    suffix = f".{base}"
    if bare_host.endswith(suffix):
        return bare_host[: -len(suffix)]
    return None


def get_store_from_host(request: Request, db: Session = Depends(get_db)) -> Store:
    """Resolve the Store for the current request's Host header.

    Supports both "<subdomain>.<BASE_DOMAIN>" hosts and verified custom domains.
    Raises 404 if the host does not map to any store.
    """
    host = request.headers.get("host", "")
    bare_host = host.split(":")[0].lower()

    subdomain = extract_subdomain(host)
    store = store_crud.get_by_subdomain(db, subdomain) if subdomain else store_crud.get_by_custom_domain(db, bare_host)

    if store is None:
        raise HTTPException(status_code=404, detail="No store found for this domain")
    return store
