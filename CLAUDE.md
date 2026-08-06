# python-backend — FastAPI

Own git repo (remote: `fast-blog`) — separate from `nextjs-frontend`, see [../CLAUDE.md](../CLAUDE.md) for the two-repo layout and how the two run together locally.

[FEATURES.md](FEATURES.md) is the source of truth for *why* the data model looks the way it does (multi-tenancy, per-store roles/permissions, refresh-token rotation, catalog restructuring) — check its "Implementation Log" section before treating an architecture choice as arbitrary or a missing feature as unplanned.

## Running locally

- Always use the repo's `venv`, never system Python (global Python here has none of the deps installed):
  `venv/Scripts/uvicorn.exe app.main:app --reload --port 8001`
- Requires Postgres running locally with the DB from `.env`'s `DATABASE_URL` (`fastblog`).
- Migrations: `venv/Scripts/alembic.exe upgrade head` / `venv/Scripts/alembic.exe revision --autogenerate -m "..."`.
- Tests: `venv/Scripts/pytest.exe` (config in `pytest.ini`, `pythonpath = .`).
- Demo/superadmin accounts are seeded via `app/scripts/seed_superadmin.py` + the alembic seed migration (`alembic/versions/5d6f833bbb09_seed_demo_login_accounts.py`) — don't hand-create these users again.

## Structure

- `app/api/` — one router module per resource (`auth`, `store`, `staff`, `product`, `category`, `brand`, `order`, `analytics`, `admin`, `plan`, `site_content`, `posts`, `comment`), all mounted under `/api/v1` in `app/main.py`.
- `app/models/` — SQLAlchemy models. Notable: `store.py`, `store_membership.py` (per-store role linking a user to a store), `product_variant.py` (price/stock live on the variant, not the parent `Product`), `refresh_token.py` (hash-only storage, see below).
- `app/core/tenant.py` — subdomain/custom-domain → `Store` resolution from the `Host` header; mirrored by the frontend's `proxy.ts`, see root CLAUDE.md.
- `app/core/permissions.py` — the `Permission` enum + `ROLE_PERMISSIONS` mapping (`owner`/`manager`/`staff`/`support`). Add new permissions/roles here, not by touching individual endpoints.
- `app/crud/` — generic `CRUDBase` pattern; extend rather than re-writing CRUD boilerplate for new models.

## Things easy to get wrong

- **Refresh tokens are rotated**: every `/api/v1/refresh` call revokes the old token and issues a new pair; reusing a revoked token 401s (replay protection). The raw token is never stored, only its SHA-256 hash.
- **`BASE_DOMAIN`** must match the frontend's `BASE_DOMAIN`/`NEXT_PUBLIC_BASE_DOMAIN` exactly (`localhost` locally, the real domain in prod) or `/api/v1/stores/resolve` won't find the store for a given host — see root CLAUDE.md's subdomain-routing section.
