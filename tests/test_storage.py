import httpx

from fda_letters import storage
from fda_letters.storage import known_urls, open_db, update


def raw(slug, issued):
    link = f'<a href="/warning-letters/{slug}">{slug}</a>'
    date = f'<time datetime="{issued}T12:00:00Z">x</time>'
    return [date, date, link, "office", "subject", "", ""]


def test_broken_letter_is_skipped_not_fatal(tmp_path, monkeypatch):
    def fetch_letter(url):
        if url.endswith("broken"):
            request = httpx.Request("GET", url)
            raise httpx.HTTPStatusError(
                "302", request=request, response=httpx.Response(302, request=request)
            )
        return {"text": "21 CFR 211.22"}

    rows = [
        raw("good-a", "2026-01-03"),
        raw("broken", "2026-01-02"),
        raw("good-b", "2026-01-01"),
    ]
    monkeypatch.setattr(storage, "fetch_index", lambda: rows)
    monkeypatch.setattr(storage, "fetch_letter", fetch_letter)
    monkeypatch.setattr(storage.time, "sleep", lambda _: None)

    db = open_db(tmp_path / "letters.db")
    saved, failed = update(db)
    assert saved == 2
    assert failed == ["https://www.fda.gov/warning-letters/broken"]
    assert len(known_urls(db)) == 2
