from fda_letters.letter import CLIENT
import time
import re

URL = "https://www.fda.gov/datatables/views/ajax"

PARAMS = {
    "_drupal_ajax": 1,
    "_wrapper_format": "drupal_ajax",
    "view_name": "warning_letter_solr_index",
    "view_display_id": "warning_letter_solr_block",
    "start": 0,
    "length": 3,
}

def clean(cell):
    # Remove HTML tags and leading/trailing whitespace
    return re.sub(r"<[^>]*>", "", cell).strip()

def date_in(cell):
    # Extract date in YYYY-MM-DD format from datetime attribute
    match = re.search(r'datetime="(\d{4}-\d{2}-\d{2})', cell)
    if match: 
        return match.group(1)
    return None

def parse_row(row):    
    link = re.search(r'href="([^"]+)"', row[2]).group(1)
    return {
        "posted": date_in(row[0]),
        "issued": date_in(row[1]),
        "company": clean(row[2]),
        "url": "https://www.fda.gov" + link,
        "office": clean(row[3]),
        "subject": clean(row[4]),
        "closeout": date_in(row[6]),
    }

def fetch_index():
    """Download every letter row from fda.gov, 500 per request."""
    
    rows = []
    start = 0
    while True:
        params = PARAMS | {"start": start, "length": 500}
        page = CLIENT.get(URL, params=params).json()
        if not page["data"]:
            break
        rows.extend(page["data"])
        start += 500
        time.sleep(1)
    return rows

if __name__ == "__main__":
    rows = fetch_index()
    print(len(rows))
    print(parse_row(rows[0]))