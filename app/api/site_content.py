from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.site_content import site_content as site_content_crud
from app.crud.site_feature import site_feature as site_feature_crud
from app.db.session import get_db
from app.schemas.site_content import SiteContentPublicRead

router = APIRouter(tags=["site-content"])


@router.get("/site-content", response_model=SiteContentPublicRead)
def read_site_content(db: Session = Depends(get_db)):
    return SiteContentPublicRead(
        hero=site_content_crud.get(db),
        features=site_feature_crud.get_all_ordered(db),
    )
