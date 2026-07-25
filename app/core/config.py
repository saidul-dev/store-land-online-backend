from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fast Blog API"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Base domain the platform is served on, e.g. stores live at "<subdomain>.<BASE_DOMAIN>"
    BASE_DOMAIN: str = "yourapp.com"
    # Comma-separated list of allowed CORS origins, or "*" for all
    BACKEND_CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_origins(self) -> list[str]:
        if self.BACKEND_CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
