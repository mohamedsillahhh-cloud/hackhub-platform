from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "HackHub"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Hackathon Management Platform"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/hackhub"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-this-secret-key-in-production"
    ENVIRONMENT: str = "development"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@hackhub.com"

    TELEGRAM_BOT_TOKEN: str = ""
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    OPENAI_API_KEY: str = ""

    AI_RATE_LIMIT_ASK: str = "20/minute"
    AI_RATE_LIMIT_EVALUATE: str = "5/minute"
    AI_RATE_LIMIT_SUGGEST: str = "3/minute"
    AI_DAILY_TOKEN_LIMIT: int = 100000

    PLAN_LIMITS: dict = {
        "free": {"max_events": 3, "max_participants": 100, "ai_enabled": False, "custom_domain": False},
        "pro": {"max_events": 20, "max_participants": 500, "ai_enabled": True, "custom_domain": False},
        "enterprise": {"max_events": -1, "max_participants": -1, "ai_enabled": True, "custom_domain": True},
    }

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
