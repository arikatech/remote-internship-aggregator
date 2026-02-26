from __future__ import annotations

import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import settings

log = logging.getLogger("migrations")


def run_migrations_if_enabled() -> None:
    enabled = os.getenv("RUN_MIGRATIONS_ON_STARTUP", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    log.info("migrations flag", extra={"RUN_MIGRATIONS_ON_STARTUP": enabled})

    if not enabled:
        return

    try:
        # project root: /app
        root = Path(__file__).resolve().parents[2]  # /app
        alembic_ini = root / "alembic.ini"
        alembic_dir = root / "alembic"

        log.info(
            "running migrations",
            extra={
                "alembic_ini": str(alembic_ini),
                "alembic_dir": str(alembic_dir),
                "db": f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}",
            },
        )

        cfg = Config(str(alembic_ini))
        cfg.set_main_option("script_location", str(alembic_dir))

        # Force Alembic to run against the *current* env vars on Render
        cfg.set_main_option("sqlalchemy.url", settings.database_url)

        command.upgrade(cfg, "head")

        log.info("migrations complete")
    except Exception as e:
        log.exception("migrations failed", extra={"error": str(e)})