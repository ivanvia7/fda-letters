import argparse

from fda_letters.export import to_csv, to_jsonl
from fda_letters.storage import open_db, update

def main() -> None:
    parser = argparse.ArgumentParser(prog="fda-letters")
    parser.add_argument("--out", required=True, help="letters.csv or letters.jsonl")
    parser.add_argument("--limit", type=int, help="stop after this many new letters")
    parser.add_argument("--since", default="", help="only letters issued on or after YYYY-MM-DD")
    args = parser.parse_args()

    db = open_db()
    print(update(db, args.limit, args.since), "new letters")
    if args.out.endswith(".csv"):
        to_csv(db, args.out, args.since)
    else:
        to_jsonl(db, args.out, args.since)