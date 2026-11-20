import html
import re
import time
from typing import Any

from fda_letters.letter import get

URL = "https://www.fda.gov/datatables/views/ajax"

PARAMS: dict[str, str | int] = {
    "_drupal_ajax": 1,
    "_wrapper_format": "drupal_ajax",
    "view_name": "warning_letter_solr_index",
    "view_display_id": "warning_letter_solr_block",
    "start": 0,
}


def clean(cell: str) -> str:
    # Remove HTML tags, decode &amp; and the like, trim whitespace
    return html.unescape(re.sub(r"<[^>]*>", "", cell)).strip()


def date_in(cell: str) -> str | None:
    # Extract date in YYYY-MM-DD format from datetime attribute
    match = re.search(r'datetime="(\d{4}-\d{2}-\d{2})', cell)
    return match.group(1) if match else None


def parse_row(row: list[str]) -> dict[str, Any]:
    link = re.search(r'href="([^"]+)"', row[2])
    if link is None:
        raise ValueError(f"no letter link in index row: {row[2]!r}")
    return {
        "posted": date_in(row[0]),
        "issued": date_in(row[1]),
        "company": clean(row[2]),
        "url": "https://www.fda.gov" + link.group(1),
        "office": clean(row[3]),
        "subject": clean(row[4]),
        "closeout": date_in(row[6]),
    }


def fetch_index() -> list[list[str]]:
    """Download every letter row from fda.gov, 500 per request."""

    rows: list[list[str]] = []
    start = 0
    while True:
        page = get(URL, **(PARAMS | {"start": start, "length": 500})).json()
        if not page["data"]:
            break
        rows.extend(page["data"])
        start += 500
        time.sleep(1)
    return rows
