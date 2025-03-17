# app/config.py
import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator
)


class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Supply Chain Orchestrator"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Advanced inventory and supply chain management system"
    
    # Server settings
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # Environment settings
    ENVIRONMENT: str = "development"  # development, staging, production, test
    DEBUG: bool = True
    
    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[PostgresDsn] = None
    SQL_ECHO: bool = False
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Build database URL from components."""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Build Redis URL from components."""
        if isinstance(v, str):
            return v
        password_part = (
            f":{values.get('REDIS_PASSWORD')}@" if values.get("REDIS_PASSWORD") else ""
        )
        return f"redis://{password_part}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}"
    
    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """Default from name to project name."""
        if not v:
            return values["PROJECT_NAME"]
        return v
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Analytics settings
    FORECASTING_HORIZON_DAYS: int = 90  # Predict inventory needs for the next 90 days
    
    # User registration
    USERS_OPEN_REGISTRATION: bool = False
    
    class Config:
        """Pydantic configuration."""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Load settings based on environment
settings = Settings()