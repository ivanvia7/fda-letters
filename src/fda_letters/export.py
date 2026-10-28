import csv
import json

from fda_letters.storage import open_db

COLUMNS = ["posted", "issued", "company", "url", "office", "subject",
           "closeout", "Product", "Recipient", "Delivery Method"]

def to_csv(db, path):
    """Write one CSV line per saved letter; the full text stays out."""
    
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row, letter in db.execute("SELECT row, letter FROM letters"):
            writer.writerow(json.loads(row) | json.loads(letter))
            
def to_jsonl(db, path):
    """Write one JSON object per saved letter; text included."""

    with open(path, "w", encoding="utf-8") as f:
        for row, letter in db.execute("SELECT row, letter FROM letters"):
            f.write(json.dumps(json.loads(row) | json.loads(letter)) + "\n")
            
if __name__ == "__main__":
    db = open_db()
    to_csv(db, "letters.csv")
    to_jsonl(db, "letters.jsonl")