from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Minimum acceptable SECRET_KEY length for production.
# Changing this constant requires updating the corresponding validator.
MIN_SECRET_KEY_LENGTH: int = 32


class Settings(BaseSettings):
    PROJECT_NAME: str = "Workforce Intelligence API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Security / Auth
    # Keep the default empty so production cannot silently run with a known key.
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str

    # HTTP Security
    # Set TRUSTED_HOST_ENABLED=true and provide comma-separated TRUSTED_HOSTS
    # in production to enable FastAPI's TrustedHostMiddleware.
    # Leave disabled in development to avoid blocking localhost requests.
    TRUSTED_HOST_ENABLED: bool = False
    TRUSTED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Rate limiting placeholder — no enforcement currently.
    # Set to True when a rate-limiting backend (e.g. slowapi) is introduced.
    RATE_LIMIT_ENABLED: bool = False

    # Report Scheduler
    REPORT_SCHEDULER_ENABLED: bool = False
    REPORT_SCHEDULER_INTERVAL_SECONDS: int = 60
    REPORT_STORAGE_PATH: str = "./storage/reports"
    REPORT_STALE_RUN_TIMEOUT_MINUTES: int = 60
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        allowed = {"HS256", "RS256"}
        if value not in allowed:
            raise ValueError(f"ALGORITHM must be one of {allowed}")
        return value

    @property
    def JWT_ALGORITHM(self) -> str:
        return self.ALGORITHM

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if not value or value.strip() == "":
            raise ValueError("SECRET_KEY must be configured in the environment.")
        if len(value) < MIN_SECRET_KEY_LENGTH:
            raise ValueError(f"SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters long.")
        
        unsafe_secrets = {
            "super-secret-production-key-change-in-env",
            "change-me",
            "changeme",
            "secret",
            "password",
            "default-secret"
        }
        if value in unsafe_secrets:
            raise ValueError("SECRET_KEY uses a known unsafe placeholder value.")
            
        return value

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value or value.strip() == "":
            raise ValueError("DATABASE_URL must be configured in the environment.")
        return value

    @field_validator("TRUSTED_HOSTS", mode="before")
    @classmethod
    def assemble_trusted_hosts(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str) and not value.startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]
        raise ValueError(value)

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str) and not value.startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]
        raise ValueError(value)

    from pydantic import model_validator
    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.ENVIRONMENT == "production":
            if self.DATABASE_URL.startswith("sqlite"):
                raise ValueError("SQLite is not allowed in production (DATABASE_URL).")
            if self.ACCESS_TOKEN_EXPIRE_MINUTES > 60:
                raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES cannot exceed 60 in production.")
            if "*" in self.BACKEND_CORS_ORIGINS:
                import warnings
                warnings.warn("Wildcard CORS ('*') is discouraged in production.")
                
        if self.REPORT_SCHEDULER_ENABLED:
            import os
            storage_path = os.path.abspath(self.REPORT_SCHEDULER_PATH if hasattr(self, 'REPORT_SCHEDULER_PATH') else self.REPORT_STORAGE_PATH)
            if os.path.isfile(storage_path):
                raise ValueError(f"REPORT_STORAGE_PATH ({storage_path}) exists as a file, must be a directory.")
            # In production, we typically want to ensure we can create or write to it.
            # We can try to make the dir to prove it's writable, or at least it doesn't fail.
            try:
                os.makedirs(storage_path, exist_ok=True)
                test_file = os.path.join(storage_path, ".test_write")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
            except Exception as e:
                raise ValueError(f"REPORT_STORAGE_PATH ({storage_path}) is not writable: {e}")

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
