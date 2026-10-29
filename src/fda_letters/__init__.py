import argparse

from fda_letters.export import to_csv, to_jsonl
from fda_letters.storage import open_db, update
from fda_letters.web import serve


def main() -> None:
    parser = argparse.ArgumentParser(prog="fda-letters")
    parser.add_argument("--out", help="letters.csv or letters.jsonl")
    parser.add_argument("--limit", type=int, help="stop after this many new letters")
    parser.add_argument(
        "--since", default="", help="only letters issued on or after YYYY-MM-DD"
    )
    parser.add_argument(
        "--serve", action="store_true", help="open a web page on localhost:8000"
    )
    args = parser.parse_args()
    if args.serve:
        serve()
        return
    if not args.out or not args.out.endswith((".csv", ".jsonl")):
        parser.error("--out must end with .csv or .jsonl")

    db = open_db()
    print(update(db, args.limit, args.since), "new letters")
    if args.out.endswith(".csv"):
        to_csv(db, args.out, args.since)
    else:
        to_jsonl(db, args.out, args.since)
