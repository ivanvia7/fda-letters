import httpx 
from selectolax.lexbor import LexborHTMLParser

CLIENT = httpx.Client(
    headers={"User-Agent": "fda-letters/0.1 (open-source FDA letter archive)"},
    timeout=30,
    transport=httpx.HTTPTransport(local_address="0.0.0.0", retries=3),
)

def parse_letter(html): 
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
            text = " ".join(node.text(separator=" ").split()) if node.tag == "dd" else ""
            if text:
                parts.append(text)
            node = node.next
        fields[label.text(strip=True).rstrip(":")] = ", ".join(parts)
    
    body = page.css_first("div[role=main]")
    lines = body.text(separator="\n", strip=True).splitlines()
    
    fields["text"] = "\n".join(line for line in lines if line.strip())
    return fields


def fetch_letter(url):
   return parse_letter(CLIENT.get(url).text)

if __name__ == "__main__":
    url = "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/rohto-pharmaceutical-co-ltd-733215-10142026"
    letter = fetch_letter(url)
    for key, value in letter.items():
        print(key, "=", value[:80])