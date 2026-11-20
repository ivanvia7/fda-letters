"""Draw 25 random bare "21 CFR 312"-style part matches from a letters.db.

Used once on 2026-11-20 against a letters.db of 708 letters (104 bare matches),
seed 3, to make tests/fixtures/eval/bare_parts_sample.jsonl. A different
letters.db gives a different sample. Each row's verdict was then set by hand.

    uv run python scripts/bare_parts_sample.py letters.db > sample.jsonl
"""

import json
import random
import re
import sqlite3
import sys

from fda_letters.citations import CFR_PART, normalize

db = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
hits = []
for url, letter in db.execute("SELECT url, letter FROM letters ORDER BY url"):
    text = normalize(json.loads(letter)["text"])
    for m in CFR_PART.finditer(text):
        if not re.search(r"[Pp]art", m.group(0)):
            context = text[max(0, m.start() - 50) : m.end() + 20].replace("\n", " ")
            hits.append(
                {
                    "url": url,
                    "match": m.group(0),
                    "parts": m.group(1),
                    "context": context,
                }
            )
print(
    f"{db.execute('SELECT count(*) FROM letters').fetchone()[0]} letters,"
    f" {len(hits)} bare matches",
    file=sys.stderr,
)
random.seed(3)
for hit in random.sample(hits, 25):
    print(json.dumps(hit | {"verdict": ""}))
