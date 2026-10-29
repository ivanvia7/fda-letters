import csv
import json

from fda_letters.citations import cfr_rules, usc_sections

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
    "usc",
]
# Letters issued on or after a YYYY-MM-DD date; "" keeps every letter.
SINCE = "SELECT row, letter FROM letters WHERE json_extract(row, '$.issued') >= ?"


def to_csv(db, path, since=""):
    """Write one CSV line per saved letter; the full text stays out."""

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row, letter in db.execute(SINCE, (since,)):
            letter = json.loads(letter)
            writer.writerow(
                json.loads(row)
                | letter
                | {
                    "cfr": "; ".join(cfr_rules(letter["text"])),
                    "usc": "; ".join(usc_sections(letter["text"])),
                }
            )


def to_jsonl(db, path, since=""):
    """Write one JSON object per saved letter; text included."""

    with open(path, "w", encoding="utf-8") as f:
        for row, letter in db.execute(SINCE, (since,)):
            f.write(json.dumps(json.loads(row) | json.loads(letter)) + "\n")
