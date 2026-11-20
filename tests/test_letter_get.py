import httpx

from fda_letters import letter


def test_get_keeps_query_in_url(monkeypatch):
    seen = []

    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(200)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(letter, "CLIENT", client)
    letter.get("https://www.fda.gov/x?a=1")
    letter.get("https://www.fda.gov/y", start=500)
    assert seen == ["https://www.fda.gov/x?a=1", "https://www.fda.gov/y?start=500"]
