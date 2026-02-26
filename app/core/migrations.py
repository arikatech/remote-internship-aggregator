from __future__ import annotations

import logging
import os
import subprocess

log = logging.getLogger("migrations")


def run_migrations_if_enabled() -> None:
    """
    Free-tier workaround: run Alembic at app startup.
    Controlled by RUN_MIGRATIONS_ON_STARTUP=true
    """
    enabled = os.getenv("RUN_MIGRATIONS_ON_STARTUP", "").lower() in {"1", "true", "yes"}
    if not enabled:
        return

    log.info("running migrations (alembic upgrade head)")
    try:
        subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
        )
        log.info("migrations complete")
    except Exception as e:
        log.exception("migrations failed", extra={"error": str(e)})
        # Don't crash the whole app; but your DB tables won't exist.
        # If you want to fail hard, uncomment:
        # raise