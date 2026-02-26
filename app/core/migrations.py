from __future__ import annotations

import logging
import os

from alembic import command
from alembic.config import Config

log = logging.getLogger("migrations")


def run_migrations_if_enabled() -> None:
    enabled = os.getenv("RUN_MIGRATIONS_ON_STARTUP", "").lower() in {"1", "true", "yes"}
    if not enabled:
        log.info("migrations disabled (RUN_MIGRATIONS_ON_STARTUP not true)")
        return

    try:
        log.info("running migrations via alembic API: upgrade head")

        alembic_cfg = Config("alembic.ini")
        # Ensure Alembic sees the right config file paths
        alembic_cfg.set_main_option("script_location", "alembic")

        command.upgrade(alembic_cfg, "head")

        log.info("migrations complete")
    except Exception as e:
        log.exception("migrations failed", extra={"error": str(e)})
        # For now we don't crash the app; but tables won't exist if this fails.