import csv
import json

from fda_letters.export import COLUMNS, to_csv, to_jsonl
from fda_letters.storage import open_db, save

TEXT = "21 CFR 211.22 and 21 CFR 801.3. 21 U.S.C. 331(a) and 355(b)."


def row(company, issued):
    return {"url": company, "company": company, "subject": "s", "issued": issued}


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_csv_header_and_bom(tmp_path):
    db = open_db(tmp_path / "letters.db")
    save(db, row("Acme", "2026-01-02"), {"text": TEXT})
    to_csv(db, tmp_path / "out.csv")
    assert (tmp_path / "out.csv").read_bytes().startswith(b"\xef\xbb\xbf")
    with open(tmp_path / "out.csv", newline="", encoding="utf-8-sig") as f:
        assert next(csv.reader(f)) == COLUMNS


def test_csv_drops_extra_keys_and_joins_citations(tmp_path):
    db = open_db(tmp_path / "letters.db")
    save(db, row("Acme", "2026-01-02"), {"text": TEXT, "extra": "x"})
    to_csv(db, tmp_path / "out.csv")
    [r] = read_csv(tmp_path / "out.csv")
    assert list(r) == COLUMNS
    assert "text" not in r and "extra" not in r
    assert r["company"] == "Acme"
    assert r["cfr"] == "211.22; 801.3"
    assert r["usc"] == "331; 355"


def test_jsonl_one_line_per_letter_letter_wins(tmp_path):
    db = open_db(tmp_path / "letters.db")
    first = row("Acme", "2026-01-02") | {"text": "row text"}
    save(db, first, {"text": TEXT, "subject": "L"})
    save(db, row("Beta", "2025-01-02"), {"text": "b"})
    to_jsonl(db, tmp_path / "out.jsonl")
    rows = {r["company"]: r for r in read_jsonl(tmp_path / "out.jsonl")}
    assert len(rows) == 2
    assert rows["Acme"]["text"] == TEXT
    assert rows["Acme"]["subject"] == "L"
    assert rows["Acme"]["cfr"] == "211.22; 801.3"
    assert rows["Acme"]["usc"] == "331; 355"
    assert rows["Beta"]["text"] == "b"


def test_since_filter(tmp_path):
    db = open_db(tmp_path / "letters.db")
    save(db, row("New", "2026-01-02"), {"text": ""})
    save(db, row("Old", "2025-01-02"), {"text": ""})
    to_csv(db, tmp_path / "out.csv", since="2026-01-01")
    assert [r["company"] for r in read_csv(tmp_path / "out.csv")] == ["New"]
    to_jsonl(db, tmp_path / "out.jsonl", since="2026-01-01")
    assert [r["company"] for r in read_jsonl(tmp_path / "out.jsonl")] == ["New"]
    to_csv(db, tmp_path / "all.csv")
    assert len(read_csv(tmp_path / "all.csv")) == 2
