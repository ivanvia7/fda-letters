import httpx 
from selectolax.lexbor import LexborHTMLParser

def parse_letter(html): 
    page = LexborHTMLParser(html)
    fields = {}
    
    for label, value in zip(page.css("dt"), page.css("dt + dd")):
        name = label.text(strip=True).rstrip(":")
        fields[name] = " ".join(value.text().split())
    
    body = page.css_first("div[role=main]")
    lines = body.text(separator="\n", strip=True).splitlines()
    
    fields["text"] = "\n".join(line for line in lines if line.strip())
    return fields


def fetch_letter(url):
    return parse_letter(httpx.get(url, timeout=30).text)

if __name__ == "__main__":
    url = "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/rohto-pharmaceutical-co-ltd-733215-10142026"
    letter = fetch_letter(url)
    for key, value in letter.items():
        print(key, "=", value[:80])