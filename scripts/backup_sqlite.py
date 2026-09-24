#!/usr/bin/env python3
import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a consistent online backup of the HackHub SQLite database.")
    parser.add_argument("database", type=Path, help="Path to the live SQLite database")
    parser.add_argument("destination", type=Path, help="Directory where backups are stored")
    args = parser.parse_args()

    database = args.database.resolve(strict=True)
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = destination / f"hackhub-{timestamp}.db"

    with sqlite3.connect(database) as source, sqlite3.connect(backup) as target:
        source.backup(target)
        result = target.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise RuntimeError(f"Backup integrity check failed: {result}")

    print(backup)


if __name__ == "__main__":
    main()
