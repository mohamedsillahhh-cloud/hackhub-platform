from typing import List

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "HackHub"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Hackathon Management Platform"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./hackhub.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TIMEOUT_SECONDS: float = 0.5

    SECRET_KEY: str = "change-this-secret-key-in-production"
    ENVIRONMENT: str = "development"
    APP_URL: str = "http://localhost:3000"
    TRUSTED_HOSTS: str = "localhost,127.0.0.1,test"
    AUTO_CREATE_TABLES: bool = True
    LOG_LEVEL: str = "INFO"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    AUTH_RATE_LIMIT_LOGIN: str = "10/minute"
    AUTH_RATE_LIMIT_REGISTER: str = "10/minute"
    AUTH_RATE_LIMIT_RESET: str = "5/minute"
    AUTH_RATE_LIMIT_REFRESH: str = "30/minute"

    SMTP_SERVER: str = Field(
        default="smtp.gmail.com",
        validation_alias=AliasChoices("SMTP_SERVER", "SMTP_HOST"),
    )
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_USERNAME", "SMTP_USER"),
    )
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
        "free": {
            "max_events": 3,
            "max_participants": 100,
            "ai_enabled": False,
            "custom_domain": False,
        },
        "pro": {
            "max_events": 20,
            "max_participants": 500,
            "ai_enabled": True,
            "custom_domain": False,
        },
        "enterprise": {
            "max_events": -1,
            "max_participants": -1,
            "ai_enabled": True,
            "custom_domain": True,
        },
    }

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def cookie_secure(self) -> bool:
        return self.ENVIRONMENT.lower() not in {"development", "test"}

    @property
    def trusted_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.TRUSTED_HOSTS.split(",") if host.strip()]

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.ENVIRONMENT.lower() not in {"development", "test"}:
            weak_secrets = {
                "change-this-secret-key-in-production",
                "super-secret-key-change-in-production",
            }
            if self.SECRET_KEY in weak_secrets or len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must contain at least 32 characters outside development/test")
            if not self.APP_URL.startswith("https://"):
                raise ValueError("APP_URL must use HTTPS outside development/test")
            if any(origin.startswith("http://") for origin in self.cors_origins_list):
                raise ValueError("CORS_ORIGINS must use HTTPS outside development/test")
            if self.AUTO_CREATE_TABLES:
                raise ValueError("AUTO_CREATE_TABLES must be false outside development/test; use Alembic migrations")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
