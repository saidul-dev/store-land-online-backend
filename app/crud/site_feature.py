from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.site_feature import SiteFeature
from app.schemas.site_content import SiteFeatureCreate, SiteFeatureUpdate


class CRUDSiteFeature(CRUDBase[SiteFeature, SiteFeatureCreate, SiteFeatureUpdate]):
    def get_all_ordered(self, db: Session) -> list[SiteFeature]:
        return db.query(SiteFeature).order_by(SiteFeature.sort_order, SiteFeature.id).all()


site_feature = CRUDSiteFeature(SiteFeature)
