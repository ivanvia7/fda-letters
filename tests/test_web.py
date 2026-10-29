import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from fda_letters.index import clean
from fda_letters.storage import open_db, save
from fda_letters.web import Handler


def row(company, issued):
    return {"url": company, "company": company, "subject": "s", "issued": issued}


def serve(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    db = open_db()
    save(db, row("Bausch & Lomb", "2026-01-02"), {"text": ""})
    save(db, row("100% Pure", "2025-01-02"), {"text": ""})
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_port}"


def post(url, body, origin=None):
    headers = {"Origin": origin} if origin else {}
    try:
        return urlopen(Request(url, body.encode(), headers)).status
    except HTTPError as error:
        return error.code


def test_clean_decodes_entities():
    assert clean("<a>Bausch &amp; Lomb</a>") == "Bausch & Lomb"


def test_page(tmp_path, monkeypatch):
    base = serve(tmp_path, monkeypatch)
    search = json.load(urlopen(base + "/letters?q=%25"))
    assert [r["company"] for r in search["rows"]] == ["100% Pure"]
    assert json.load(urlopen(base + "/letters?q=Bausch+%26"))["total"] == 1

    (tmp_path / "letters.csv").write_text("fetched")
    assert b"Bausch & Lomb" in urlopen(base + "/export.csv").read()
    assert (tmp_path / "letters.csv").read_text() == "fetched"

    assert urlopen(base + "/status?x=1").status == 200
    assert post(base + "/start", "", "https://evil.example") == 403
    assert post(base + "/start", "", "http://localhost:3000") == 403
    assert post(base + "/start", "limit=abc") == 400
    assert post(base + "/start", "limit=0") == 400
    assert post(base + "/start", "limit=%C2%B2") == 400
    assert post(base + "/start", "since=yesterday") == 400
