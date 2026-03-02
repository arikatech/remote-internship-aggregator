from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Remote Internship Aggregator"
    env: str = "dev"
    log_level: str = "INFO"

    # DB
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "internships"
    postgres_user: str = "intern"
    postgres_password: str = "internpass"

    # Telegram
    telegram_bot_token: str | None = None

    # Scheduler (Milestone 6)
    ops_ingest_key: str | None = None
    scheduler_enabled: bool = True
    scheduler_timezone: str = "Europe/Rome"
    scheduler_ingest_cron: str = "0 9 * * *"  # minute hour day month day-of-week
    scheduler_ingest_jitter_seconds: int = 30

    # Cross-process safety (recommended if you ever run multiple workers/containers)
    # Uses Postgres advisory locks
    scheduler_use_db_lock: bool = True
    scheduler_db_lock_key: int = 424242

    # HTTP fetch hardening (connectors)
    http_timeout_seconds: int = 15
    http_max_retries: int = 2

    @property
    def database_url(self) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()