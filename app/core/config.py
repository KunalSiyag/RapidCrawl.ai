from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RapidCrawl.ai"
    app_env: str = "development"
    request_timeout_seconds: float = 10.0
    max_competitor_urls: int = 3

    model_config = SettingsConfigDict(env_prefix="RAPIDCRAWL_", extra="ignore")


settings = Settings()
