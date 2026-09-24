import sqlite3
import subprocess
from pathlib import Path

from app.core.config import settings

INITIAL_REVISION = "b742d814514c"
HEAD_REVISION = "d24f93a91230"
SQLITE_PREFIX = "sqlite+aiosqlite:///"


def main() -> None:
    if not settings.DATABASE_URL.startswith(SQLITE_PREFIX):
        return

    database_value = settings.DATABASE_URL.removeprefix(SQLITE_PREFIX)
    if database_value in {"", ":memory:"}:
        return

    database_path = Path(database_value)
    if not database_path.exists():
        return

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }
        if "users" not in tables or "alembic_version" in tables:
            return

        event_sql_row = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'events'"
        ).fetchone()
        event_sql = event_sql_row[0] if event_sql_row else ""
        revision = (
            HEAD_REVISION if "auth_sessions" in tables and "ck_events_date_range" in event_sql else INITIAL_REVISION
        )

    subprocess.run(["alembic", "stamp", revision], check=True)


if __name__ == "__main__":
    main()
