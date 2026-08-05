from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.plan import plan as plan_crud
from app.db.session import get_db
from app.schemas.plan import PlanRead

router = APIRouter(tags=["plans"])


@router.get("/plans", response_model=list[PlanRead])
def list_active_plans(db: Session = Depends(get_db)):
    return plan_crud.get_active(db)
