from pydantic import BaseModel


class SiteContentRead(BaseModel):
    hero_badge: str | None
    hero_heading: str
    hero_subheading: str

    class Config:
        from_attributes = True


class SiteContentUpdate(BaseModel):
    hero_badge: str | None = None
    hero_heading: str
    hero_subheading: str


class SiteFeatureRead(BaseModel):
    id: int
    icon: str
    title: str
    description: str
    sort_order: int

    class Config:
        from_attributes = True


class SiteFeatureCreate(BaseModel):
    icon: str
    title: str
    description: str
    sort_order: int = 0


class SiteFeatureUpdate(BaseModel):
    icon: str | None = None
    title: str | None = None
    description: str | None = None
    sort_order: int | None = None


class SiteContentPublicRead(BaseModel):
    hero: SiteContentRead
    features: list[SiteFeatureRead]
