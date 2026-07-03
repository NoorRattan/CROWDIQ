"""Core application configuration."""

import json
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

DEFAULT_ALLOWED_ORIGINS = [
    "https://promptwar-db092.web.app",
    "https://promptwar-db092.firebaseapp.com",
    "http://localhost:5173",
    "http://localhost:4173",
]


class CrowdIQEnvSettingsSource(EnvSettingsSource):
    """Environment source with raw ALLOWED_ORIGINS handling."""

    def prepare_field_value(
        self, field_name: str, field: Any, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == "ALLOWED_ORIGINS":
            return value
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class CrowdIQDotEnvSettingsSource(DotEnvSettingsSource):
    """Dotenv source with raw ALLOWED_ORIGINS handling."""

    def prepare_field_value(
        self, field_name: str, field: Any, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == "ALLOWED_ORIGINS":
            return value
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    """Application settings loaded from environment variables and `.env`."""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            CrowdIQEnvSettingsSource(settings_cls),
            CrowdIQDotEnvSettingsSource(settings_cls),
            file_secret_settings,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        enable_decoding=False,
    )

    APP_NAME: str = Field(default="CrowdIQ", description="Application display name")
    APP_VERSION: str = Field(default="1.0.0", description="API version string")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://test:test@localhost/test",
        description="Async PostgreSQL connection string",
    )
    REDIS_URL: str = Field(default="", description="Upstash Redis REST URL")
    REDIS_TOKEN: str = Field(default="", description="Upstash Redis REST token")

    FIREBASE_PROJECT_ID: str = Field(default="", description="Firebase project ID")
    FIREBASE_SERVICE_ACCOUNT_PATH: str = Field(
        default="/app/firebase-service-account.json",
        description="Mounted Firebase Admin service account JSON path",
    )
    FIREBASE_STORAGE_BUCKET: str = Field(
        default="",
        description="Firebase Storage bucket name",
    )

    GOOGLE_MAPS_API_KEY: str = Field(default="", description="Google Maps API key")
    GOOGLE_TRANSLATE_API_KEY: str = Field(
        default="",
        description="Google Translate API key",
    )

    ALLOWED_ORIGINS: list[str] = Field(
        default_factory=lambda: DEFAULT_ALLOWED_ORIGINS.copy(),
        description="Allowed CORS origins",
    )
    SECRET_KEY: str = Field(default="dev-secret-key", description="Application secret")
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, value: Any) -> list[str]:
        """
        Accept ALLOWED_ORIGINS as a list, JSON array string, or comma-separated string.

        Always include the known-safe deployment defaults so Firebase Hosting
        origins keep working even when Cloud Run env vars are partially configured.
        """
        origins: list[str] = []

        if isinstance(value, list):
            origins = [str(origin).strip() for origin in value if str(origin).strip()]
        elif isinstance(value, str):
            value = value.strip()
            if not value:
                origins = []
            elif value.startswith("["):
                try:
                    parsed = json.loads(value)
                    origins = [
                        str(origin).strip() for origin in parsed if str(origin).strip()
                    ]
                except Exception:
                    origins = []
            else:
                origins = [
                    origin.strip() for origin in value.split(",") if origin.strip()
                ]

        for required_origin in DEFAULT_ALLOWED_ORIGINS:
            if required_origin not in origins:
                origins.append(required_origin)

        return origins or DEFAULT_ALLOWED_ORIGINS.copy()

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Normalize Postgres URLs to the asyncpg SQLAlchemy dialect."""
        if value.startswith("postgres://"):
            value = f"postgresql://{value[len('postgres://'):]}"
        if value.startswith("postgresql://"):
            value = value.replace("postgresql://", "postgresql+asyncpg://", 1)
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must start with postgresql+asyncpg://")
        return value


settings = Settings()
