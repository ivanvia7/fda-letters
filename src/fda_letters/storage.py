import json
import sqlite3
import sys
import time
from collections.abc import Callable
from os import PathLike
from typing import Any

import httpx

from fda_letters.index import fetch_index, parse_row
from fda_letters.letter import fetch_letter


def open_db(path: str | PathLike[str] = "letters.db") -> sqlite3.Connection:
    """Open the local letter cache, creating it on first use."""
    db = sqlite3.connect(path)
    db.execute(
        "CREATE TABLE IF NOT EXISTS letters "
        "(url TEXT PRIMARY KEY, row TEXT, letter TEXT)"
    )
    return db


def save(db: sqlite3.Connection, row: dict[str, Any], letter: dict[str, Any]) -> None:
    "Store one letter; saving the same URL will overwrite the existing entry."
    db.execute(
        "INSERT OR REPLACE INTO letters (url, row, letter) VALUES (?, ?, ?)",
        (row["url"], json.dumps(row), json.dumps(letter)),
    )
    db.commit()


def known_urls(db: sqlite3.Connection) -> set[str]:
    """Return the set of letter URLs already saved."""
    return {url for (url,) in db.execute("SELECT url FROM letters")}


def update(
    db: sqlite3.Connection,
    limit: int | None = None,
    since: str = "",
    progress: Callable[[int, int], None] | None = None,
) -> tuple[int, list[str]]:
    """Save every letter not in the cache yet; return (saved, failed URLs).

    A letter page that errors is skipped, so one broken page never stops the run;
    it stays unsaved and the next run tries it again.
    progress, if given, is called as progress(done, total) after each letter.
    """
    known = known_urls(db)
    rows = [parse_row(raw) for raw in fetch_index()]
    rows = [r for r in rows if r["url"] not in known and (r["issued"] or "") >= since]
    rows = rows[:limit] if limit is not None else rows

    failed = []
    for done, row in enumerate(rows, 1):
        try:
            save(db, row, fetch_letter(row["url"]))
        except (httpx.HTTPError, ValueError) as error:
            failed.append(row["url"])
            print(f"skipped {row['url']}: {error}", file=sys.stderr)
        if progress:
            progress(done, len(rows))
        time.sleep(1)
    return len(rows) - len(failed), failed
