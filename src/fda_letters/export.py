import csv
import json
import sqlite3
from collections.abc import Iterator
from os import PathLike
from typing import Any

from fda_letters.citations import citations

COLUMNS = [
    "posted",
    "issued",
    "company",
    "url",
    "office",
    "subject",
    "closeout",
    "Product",
    "Recipient",
    "Delivery Method",
    "cfr",
    "cfr_parts",
    "usc",
]
# Letters issued on or after a YYYY-MM-DD date; "" keeps every letter.
SINCE = "SELECT row, letter FROM letters WHERE json_extract(row, '$.issued') >= ?"


Path = str | PathLike[str]


def letters(db: sqlite3.Connection, since: str) -> Iterator[dict[str, Any]]:
    """Each saved letter as one dict: index row, letter fields, then citations."""
    for row, letter in db.execute(SINCE, (since,)):
        merged = json.loads(row) | json.loads(letter)
        yield merged | citations(merged["text"])


def to_csv(db: sqlite3.Connection, path: Path, since: str = "") -> None:
    """Write one CSV line per saved letter; the full text stays out."""

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(letters(db, since))


def to_jsonl(db: sqlite3.Connection, path: Path, since: str = "") -> None:
    """Write one JSON object per saved letter; text and citations included."""

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(letter) + "\n" for letter in letters(db, since))
