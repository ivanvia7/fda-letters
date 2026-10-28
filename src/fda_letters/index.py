import httpx 
import time

URL = "https://www.fda.gov/datatables/views/ajax"

PARAMS = {
    "_drupal_ajax": 1,
    "_wrapper_format": "drupal_ajax",
    "view_name": "warning_letter_solr_index",
    "view_display_id": "warning_letter_solr_block",
    "start": 0,
    "length": 3,
}

def fetch_index():
    rows = []
    start = 0
    while True:
        params = PARAMS | {"start": start, "length": 500}
        page = httpx.get(URL, params=params, timeout=30).json()
        if not page["data"]:
            break
        rows.extend(page["data"])
        start += 500
        time.sleep(1)
    return rows

if __name__ == "__main__":
    rows = fetch_index()
    print(len(rows))