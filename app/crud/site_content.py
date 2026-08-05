from sqlalchemy.orm import Session

from app.models.site_content import SiteContent
from app.schemas.site_content import SiteContentUpdate


class CRUDSiteContent:
    def get(self, db: Session) -> SiteContent:
        obj = db.query(SiteContent).first()
        if obj is None:
            obj = SiteContent()
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj

    def update(self, db: Session, obj_in: SiteContentUpdate) -> SiteContent:
        obj = self.get(db)
        for field, value in obj_in.model_dump().items():
            setattr(obj, field, value)
        db.commit()
        db.refresh(obj)
        return obj


site_content = CRUDSiteContent()
