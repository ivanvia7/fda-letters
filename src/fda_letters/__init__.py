import argparse

from fda_letters.export import to_csv, to_jsonl
from fda_letters.storage import open_db, update

def main() -> None:
    parser = argparse.ArgumentParser(prog="fda-letters")
    parser.add_argument("--out", required=True, help="letters.csv or letters.jsonl")
    parser.add_argument("--limit", type=int, help="stop after this many new letters")
    args = parser.parse_args()

    db = open_db()
    print(update(db, args.limit), "new letters")
    if args.out.endswith(".csv"):
        to_csv(db, args.out)
    else:
        to_jsonl(db, args.out)