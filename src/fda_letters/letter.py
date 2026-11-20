import os

import httpx
from selectolax.lexbor import LexborHTMLParser

CLIENT = httpx.Client(
    headers={"User-Agent": "fda-letters/0.1 (open-source FDA letter archive)"},
    # fda.gov can take 30+ s on a cold index call.
    timeout=httpx.Timeout(90, connect=10),
    transport=httpx.HTTPTransport(
        local_address="0.0.0.0",
        retries=3,
        proxy=os.environ.get("HTTPS_PROXY"),
    ),
)


def get(url: str, **params: str | int) -> httpx.Response:
    """GET, retrying a read timeout once; transport retries cover connects only."""
    try:
        # params=None, not {}, so a query string already in the url stays.
        response = CLIENT.get(url, params=params or None)
    except httpx.ReadTimeout:
        response = CLIENT.get(url, params=params or None)
    response.raise_for_status()
    return response


def parse_letter(html: str) -> dict[str, str]:
    page = LexborHTMLParser(html)
    fields = {}
    # Drop hidden labels like "Recipient Name" so they stay out of the values.
    for hidden in page.css(".field--label"):
        hidden.decompose()

    # A label can own several <dd> cells (name, company, address, email),
    # and the first is often empty, so join every non-empty one up to the next <dt>.
    for label in page.css("dt"):
        parts = []
        node = label.next
        while node is not None and node.tag != "dt":
            text = (
                " ".join(node.text(separator=" ").split()) if node.tag == "dd" else ""
            )
            if text:
                parts.append(text)
            node = node.next
        fields[label.text(strip=True).rstrip(":")] = ", ".join(parts)

    body = page.css_first("div[role=main]")
    if body is None:
        raise ValueError("no div[role=main] on the letter page")
    lines = body.text(separator="\n", strip=True).splitlines()

    fields["text"] = "\n".join(line for line in lines if line.strip())
    return fields


def fetch_letter(url: str) -> dict[str, str]:
    return parse_letter(get(url).text)
