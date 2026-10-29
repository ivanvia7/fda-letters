import json
import sqlite3
import time

from fda_letters.index import fetch_index, parse_row
from fda_letters.letter import fetch_letter


def open_db(path="letters.db"):
    """Open the local letter cache, creating it on first use."""
    db = sqlite3.connect(path)
    db.execute(
        "CREATE TABLE IF NOT EXISTS letters "
        "(url TEXT PRIMARY KEY, row TEXT, letter TEXT)"
    )
    return db


def save(db, row, letter):
    "Store one letter; saving the same URL will overwrite the existing entry."
    db.execute(
        "INSERT OR REPLACE INTO letters (url, row, letter) VALUES (?, ?, ?)",
        (row["url"], json.dumps(row), json.dumps(letter)),
    )
    db.commit()


def known_urls(db):
    """Return the set of letter URLs already saved."""
    return {url for (url,) in db.execute("SELECT url FROM letters")}


def update(db, limit=None, since="", progress=None):
    """Save every letter not in the cache yet; return how many were new.

    progress, if given, is called as progress(done, total) after each letter.
    """
    known = known_urls(db)
    rows = [parse_row(raw) for raw in fetch_index()]
    rows = [r for r in rows if r["url"] not in known and r["issued"] >= since]
    rows = rows[:limit] if limit is not None else rows

    for done, row in enumerate(rows, 1):
        save(db, row, fetch_letter(row["url"]))
        if progress:
            progress(done, len(rows))
        time.sleep(1)
    return len(rows)
