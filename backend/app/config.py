from typing import List, Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


MIN_SECRET_KEY_LENGTH: int = 32


class Settings(BaseSettings):
    PROJECT_NAME: str = "Workforce Intelligence API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ─────────────────────────────────────────────────────────
    # Security / authentication
    # ─────────────────────────────────────────────────────────

    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Browser authentication cookie.
    #
    # Development:
    #   false is acceptable for local HTTP.
    #
    # Production:
    #   must be true because the application is expected to run
    #   behind HTTPS.
    AUTH_COOKIE_SECURE: bool = False
    AUTH_COOKIE_NAME: str = "access_token"
    AUTH_COOKIE_SAMESITE: str = "lax"
    AUTH_COOKIE_PATH: str = "/api/v1"

    DATABASE_URL: str

    # ─────────────────────────────────────────────────────────
    # Host security
    # ─────────────────────────────────────────────────────────

    TRUSTED_HOST_ENABLED: bool = False

    TRUSTED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
    ]

    # ─────────────────────────────────────────────────────────
    # Rate limiting
    # ─────────────────────────────────────────────────────────

    RATE_LIMIT_ENABLED: bool = False

    # Current backend is process-local memory.
    #
    # Production must use a shared/distributed implementation or
    # edge/API-gateway rate limiting before enabling the application
    # limiter across multiple workers.
    RATE_LIMIT_BACKEND: str = "memory"

    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5
    RATE_LIMIT_LOGIN_WINDOW_SECONDS: int = 60

    # ─────────────────────────────────────────────────────────
    # CSRF
    # ─────────────────────────────────────────────────────────

    CSRF_ENABLED: bool = True

    CSRF_COOKIE_NAME: str = "csrf_token"
    CSRF_HEADER_NAME: str = "X-CSRF-Token"

    # CSRF cookie must be readable by frontend JavaScript.
    CSRF_COOKIE_PATH: str = "/"

    # ─────────────────────────────────────────────────────────
    # Report scheduler
    # ─────────────────────────────────────────────────────────

    REPORT_SCHEDULER_ENABLED: bool = False
    REPORT_SCHEDULER_INTERVAL_SECONDS: int = 60

    REPORT_STORAGE_PATH: str = "./storage/reports"

    REPORT_STALE_RUN_TIMEOUT_MINUTES: int = 60

    # ─────────────────────────────────────────────────────────
    # Scheduler metrics
    # ─────────────────────────────────────────────────────────

    SCHEDULER_METRICS_ENABLED: bool = False
    SCHEDULER_METRICS_HOST: str = "127.0.0.1"
    SCHEDULER_METRICS_PORT: int = 9101

    # ─────────────────────────────────────────────────────────
    # Application metrics
    # ─────────────────────────────────────────────────────────

    # Metrics should be explicitly enabled.
    #
    # In production, expose them through a private monitoring
    # network / reverse proxy rather than directly to the public.
    METRICS_ENABLED: bool = False
    METRICS_PATH: str = "/metrics"

    # ─────────────────────────────────────────────────────────
    # CORS
    # ─────────────────────────────────────────────────────────

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # ─────────────────────────────────────────────────────────
    # Validators
    # ─────────────────────────────────────────────────────────

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(
        cls,
        value: str,
    ) -> str:
        allowed = {
            "HS256",
            "RS256",
        }

        if value not in allowed:
            raise ValueError(
                f"ALGORITHM must be one of {allowed}"
            )

        return value

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(
        cls,
        value: str,
    ) -> str:
        if not value or not value.strip():
            raise ValueError(
                "SECRET_KEY must be configured in the environment."
            )

        if len(value) < MIN_SECRET_KEY_LENGTH:
            raise ValueError(
                "SECRET_KEY must be at least "
                f"{MIN_SECRET_KEY_LENGTH} characters long."
            )

        unsafe_secrets = {
            "super-secret-production-key-change-in-env",
            "change-me",
            "changeme",
            "secret",
            "password",
            "default-secret",
        }

        if value in unsafe_secrets:
            raise ValueError(
                "SECRET_KEY uses a known unsafe placeholder value."
            )

        return value

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(
        cls,
        value: str,
    ) -> str:
        if not value or not value.strip():
            raise ValueError(
                "DATABASE_URL must be configured in the environment."
            )

        return value

    @field_validator("TRUSTED_HOSTS", mode="before")
    @classmethod
    def assemble_trusted_hosts(
        cls,
        value: Union[str, List[str]],
    ) -> List[str]:
        if isinstance(value, str) and not value.startswith("["):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            return [value]

        raise ValueError(value)

    @field_validator(
        "BACKEND_CORS_ORIGINS",
        mode="before",
    )
    @classmethod
    def assemble_cors_origins(
        cls,
        value: Union[str, List[str]],
    ) -> List[str]:
        if isinstance(value, str) and not value.startswith("["):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            return [value]

        raise ValueError(value)

    @field_validator("AUTH_COOKIE_SAMESITE")
    @classmethod
    def validate_cookie_samesite(
        cls,
        value: str,
    ) -> str:
        normalized = value.lower()

        if normalized not in {
            "lax",
            "strict",
            "none",
        }:
            raise ValueError(
                "AUTH_COOKIE_SAMESITE must be "
                "lax, strict, or none."
            )

        if normalized == "none":
            # SameSite=None requires Secure cookies in browsers.
            # Requiring production HTTPS here avoids invalid settings.
            return normalized

        return normalized

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.ENVIRONMENT == "production":
            if self.DATABASE_URL.startswith("sqlite"):
                raise ValueError(
                    "SQLite is not allowed in production "
                    "(DATABASE_URL)."
                )

            if self.ACCESS_TOKEN_EXPIRE_MINUTES > 60:
                raise ValueError(
                    "ACCESS_TOKEN_EXPIRE_MINUTES cannot exceed "
                    "60 in production."
                )

            if not self.AUTH_COOKIE_SECURE:
                raise ValueError(
                    "AUTH_COOKIE_SECURE must be true in production."
                )

            if self.CSRF_ENABLED and not self.CSRF_COOKIE_PATH == "/":
                raise ValueError(
                    "CSRF_COOKIE_PATH must be '/' for the browser CSRF cookie."
                )

            if (
                self.RATE_LIMIT_ENABLED
                and self.RATE_LIMIT_BACKEND == "memory"
            ):
                raise ValueError(
                    "Process-local memory rate limiting cannot be enabled "
                    "as the production rate-limit backend. "
                    "Use distributed/edge rate limiting first."
                )

            if self.AUTH_COOKIE_SAMESITE == "none":
                if not self.AUTH_COOKIE_SECURE:
                    raise ValueError(
                        "SameSite=None requires a secure cookie."
                    )

            if "*" in self.BACKEND_CORS_ORIGINS:
                import warnings

                warnings.warn(
                    "Wildcard CORS ('*') is discouraged in production."
                )

            if self.METRICS_ENABLED:
                import warnings

                warnings.warn(
                    "METRICS_ENABLED=true exposes the metrics endpoint. "
                    "Protect it through private networking or an "
                    "authenticated monitoring proxy."
                )

        if self.REPORT_SCHEDULER_ENABLED:
            import os

            storage_path = os.path.abspath(
                self.REPORT_STORAGE_PATH
            )

            if os.path.isfile(storage_path):
                raise ValueError(
                    "REPORT_STORAGE_PATH "
                    f"({storage_path}) exists as a file; "
                    "it must be a directory."
                )

            try:
                os.makedirs(
                    storage_path,
                    exist_ok=True,
                )

                test_file = os.path.join(
                    storage_path,
                    ".test_write",
                )

                with open(
                    test_file,
                    "w",
                    encoding="utf-8",
                ) as file:
                    file.write("test")

                os.remove(test_file)

            except Exception as exc:
                raise ValueError(
                    "REPORT_STORAGE_PATH "
                    f"({storage_path}) is not writable: {exc}"
                ) from exc

        return self

    # ─────────────────────────────────────────────────────────
    # Pydantic settings
    # ─────────────────────────────────────────────────────────

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

settings = Settings()