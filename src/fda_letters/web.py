import json
import re
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from fda_letters.citations import cfr_rules
from fda_letters.export import to_csv, to_jsonl
from fda_letters.storage import open_db, update

FILES = {"/letters.csv": "text/csv", "/letters.jsonl": "application/x-ndjson"}
STATUS = {"state": "idle", "done": 0, "total": 0, "error": ""}
ISSUED = "json_extract(row, '$.issued')"
MATCH = (
    "WHERE json_extract(row, '$.company') LIKE :q ESCAPE '\\'"
    " OR json_extract(row, '$.subject') LIKE :q ESCAPE '\\'"
)

PAGE = b"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>fda-letters</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/themes/dark.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr@4.6.13"></script>
<style>
/* Carbon g100 dark tokens, same as the task board */
:root { --bg: #161616; --layer: #262626; --layer2: #393939; --hover: #333;
  --border: #6f6f6f; --text: #f4f4f4; --text2: #c6c6c6; --helper: #a8a8a8;
  --link: #78a9ff; --blue: #0f62fe; --success: #42be65; --error: #fa4d56; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: 400 14px/20px "IBM Plex Sans", system-ui, sans-serif; letter-spacing: .16px; }
main { max-width: 960px; margin: 0 auto; padding: 48px 32px; }
h1 { font-size: 28px; line-height: 36px; font-weight: 400; margin: 0 0 4px; }
.lead { color: var(--helper); margin: 0 0 32px; }
a { color: var(--link); text-decoration: none; } a:hover { text-decoration: underline; }
.card { background: var(--layer); margin-bottom: 24px; }
.card > h2 { margin: 0; padding: 16px; font-size: 14px; font-weight: 600;
  border-bottom: 1px solid var(--layer2); display: flex; gap: 8px;
  align-items: baseline; }
.card > h2 small { color: var(--helper); font-weight: 400; }
.body { padding: 16px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
label { display: block; font-size: 12px; color: var(--text2); letter-spacing: .32px; }
input { display: block; width: 100%; margin-top: 8px; height: 40px; padding: 0 16px;
  font: inherit; color: var(--text); background: var(--layer2); border: 0;
  border-bottom: 1px solid var(--border); }
input:focus { outline: 2px solid #fff; outline-offset: -2px; }
input::placeholder { color: #6f6f6f; }
button { font: inherit; cursor: pointer; height: 40px; padding: 0 16px; border: 0;
  background: var(--blue); color: #fff; }
button:hover { background: #0050e6; } button:disabled { background: #525252;
  cursor: default; }
.sm { height: 32px; padding: 0 12px; background: none; color: var(--text);
  box-shadow: inset 0 0 0 1px var(--border); }
.sm:hover { background: var(--layer2); text-decoration: none; }
a.sm { display: inline-flex; align-items: center; font-size: 14px; }
.actions { margin-left: auto; display: flex; gap: 8px; }
.presets { display: flex; gap: 8px; margin-bottom: 24px; }
progress { appearance: none; width: 100%; height: 8px; border: 0;
  background: var(--layer2); }
progress::-webkit-progress-bar { background: var(--layer2); }
progress::-webkit-progress-value { background: var(--blue); }
progress::-moz-progress-bar { background: var(--blue); }
.status { padding: 16px; border-top: 1px solid var(--layer2); }
.status p { margin: 8px 0 0; color: var(--text2); }
table { border-collapse: collapse; width: 100%; }
th, td { padding: 8px 16px; text-align: left; vertical-align: top;
  border-bottom: 1px solid var(--layer2); }
th { background: var(--layer2); font-weight: 600; }
td { color: var(--text2); } tr:hover td { background: var(--hover); }
td:first-child { white-space: nowrap; }
.note { display: block; padding: 12px 16px; color: var(--helper); font-size: 12px; }
.search { padding: 16px; } .search input { margin: 0; }
</style>
</head>
<body>
<main>
<h1>FDA warning letters</h1>
<p class="lead">
  Fetch letters from fda.gov into a local database, then search and export them.
</p>

<section class="card">
  <h2>Fetch new letters</h2>
  <form id="start" class="body">
    <div class="grid">
      <label>Issued since <input id="since" name="since" placeholder="Any date"></label>
      <label>Max new letters
        <input type="number" name="limit" min="1" placeholder="No limit">
      </label>
    </div>
    <div class="presets">
      <button type="button" class="sm" data-days="30">Last 30 days</button>
      <button type="button" class="sm" data-days="365">Last year</button>
      <button type="button" class="sm" data-days="0">Any date</button>
    </div>
    <button id="go">Fetch new letters</button>
  </form>
  <div class="status">
    <progress id="bar" value="0" max="1"></progress>
    <p id="text"></p>
    <p id="files" hidden>
      Download <a href="/letters.csv" download>letters.csv</a> &middot;
      <a href="/letters.jsonl" download>letters.jsonl</a>
    </p>
  </div>
</section>

<section class="card">
  <h2>Saved letters <small id="stats"></small>
    <span class="actions">
      <a class="sm" href="/export.csv" download="letters.csv">CSV</a>
      <a class="sm" href="/export.jsonl" download="letters.jsonl">JSON</a>
    </span>
  </h2>
  <div class="search">
    <input type="search" id="q" placeholder="Search company or subject">
  </div>
  <table>
    <thead><tr>
      <th>Issued</th><th>Company</th><th>Subject</th><th>CFR rules</th>
    </tr></thead>
    <tbody id="rows"></tbody>
  </table>
  <small id="shown" class="note"></small>
</section>
</main>
<script>
const form = document.getElementById("start");
const bar = document.getElementById("bar");
const text = document.getElementById("text");
// Without the CDN the field stays a plain YYYY-MM-DD text box.
const since = document.getElementById("since");
const picker = window.flatpickr && flatpickr(since, {
  dateFormat: "Y-m-d", altInput: true, altFormat: "j M Y",
  minDate: "2021-01-01", maxDate: "today",
});
let lastState = "";
let error = "";  // why the last fetch did not start; poll keeps it on screen

document.querySelectorAll("[data-days]").forEach((button) => {
  button.onclick = () => {
    const days = Number(button.dataset.days);
    const day = days ? new Date(Date.now() - days * 864e5) : "";
    if (picker) picker.setDate(day);
    else since.value = day && day.toISOString().slice(0, 10);
  };
});

form.onsubmit = async (event) => {
  event.preventDefault();
  const body = new URLSearchParams(new FormData(form));
  const response = await fetch("/start", {method: "POST", body});
  error = response.ok ? "" : response.statusText;
  poll();
};

async function poll() {
  const s = await (await fetch("/status")).json();
  document.getElementById("go").disabled = s.state === "running";
  document.getElementById("files").hidden = s.state !== "done";
  if (s.state !== lastState && s.state === "done") search();  // show new rows
  lastState = s.state;
  if (s.state === "running" && s.total === 0) {
    bar.removeAttribute("value");  // no value draws the browser's moving bar
    text.textContent = "Reading the letter list from fda.gov...";
    return;
  }
  bar.max = Math.max(s.total, 1);
  bar.value = s.state === "done" ? bar.max : s.done;
  text.textContent = {
    idle: error || "Fetches only letters not saved yet. One request a second.",
    running: `${s.done} of ${s.total} new letters`,
    done: `Done. ${s.total} new letters saved.`,
    failed: `Failed: ${s.error}`,
  }[s.state];
}

async function search() {
  const q = document.getElementById("q").value;
  const data = await (await fetch("/letters?q=" + encodeURIComponent(q))).json();
  document.getElementById("stats").textContent =
    data.total ? ` ${data.total} letters, ${data.first} to ${data.last}`
               : " none found";
  document.getElementById("shown").textContent =
    `Showing ${data.rows.length} of ${data.total}, newest first.`;
  const tbody = document.getElementById("rows");
  tbody.replaceChildren(...data.rows.map((r) => {
    const tr = document.createElement("tr");
    const link = Object.assign(document.createElement("a"),
      {href: r.url, target: "_blank", textContent: r.company});
    [r.issued, link, r.subject, r.cfr].forEach((value) => {
      const td = document.createElement("td");
      td.append(value);
      tr.append(td);
    });
    return tr;
  }));
}

let timer;
document.getElementById("q").oninput = () => {
  clearTimeout(timer);
  timer = setTimeout(search, 250);
};
search();
poll();
setInterval(poll, 1000);
</script>
</body>
</html>
"""


def run(limit, since):
    """Fetch new letters in the background, then write both export files."""
    try:
        db = open_db()  # sqlite connections stay in the thread that opened them
        update(db, limit, since, lambda d, t: STATUS.update(done=d, total=t))
        to_csv(db, "letters.csv", since)
        to_jsonl(db, "letters.jsonl", since)
        STATUS["state"] = "done"
    except Exception as error:
        STATUS.update(state="failed", error=str(error))


def letters(query):
    """Count saved letters matching a search; return the 50 newest."""
    db = open_db()
    like = {"q": "%" + re.sub(r"([%_\\])", r"\\\1", query) + "%"}
    total, first, last = db.execute(
        f"SELECT count(*), min({ISSUED}), max({ISSUED}) FROM letters {MATCH}", like
    ).fetchone()
    found = db.execute(
        f"SELECT row, letter FROM letters {MATCH} ORDER BY {ISSUED} DESC LIMIT 50",
        like,
    )
    rows = [
        json.loads(row) | {"cfr": ", ".join(cfr_rules(json.loads(letter)["text"]))}
        for row, letter in found
    ]
    return {"total": total, "first": first, "last": last, "rows": rows}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        path = url.path
        if path == "/letters":
            query = parse_qs(url.query).get("q", [""])[0]
            self.reply(json.dumps(letters(query)).encode(), "application/json")
        elif path == "/":
            self.reply(PAGE, "text/html; charset=utf-8")
        elif path == "/status":
            self.reply(json.dumps(STATUS).encode(), "application/json")
        elif path in ("/export.csv", "/export.jsonl"):
            # Every saved letter, in a temp file, so the fetch result files stay.
            name = "letters" + path.removeprefix("/export")
            with tempfile.TemporaryDirectory() as folder:
                file = Path(folder, name)
                (to_csv if name.endswith(".csv") else to_jsonl)(open_db(), file)
                self.reply(file.read_bytes(), FILES["/" + name])
        elif path in FILES and Path(path[1:]).exists():
            self.reply(Path(path[1:]).read_bytes(), FILES[path])
        else:
            self.send_error(404)

    def do_POST(self):
        # Browsers send Origin on a POST, so another site cannot start a fetch.
        port = self.server.server_port
        origin = self.headers.get("Origin")
        if origin and origin not in (f"http://localhost:{port}", f"http://127.0.0.1:{port}"):
            self.send_error(403)
            return
        if self.path != "/start" or STATUS["state"] == "running":
            self.send_error(409)
            return
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode())
        limit = form.get("limit", [""])[0]
        since = form.get("since", [""])[0]
        if limit and not re.fullmatch(r"[1-9][0-9]{0,5}", limit):
            self.send_error(400, "Max new letters must be a whole number above 0")
            return
        if since and not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", since):
            self.send_error(400, "Issued since must be YYYY-MM-DD")
            return
        limit = int(limit) if limit else None
        # Set before the thread starts, so the next /status already says running.
        STATUS.update(state="running", done=0, total=0, error="")
        threading.Thread(target=run, args=(limit, since), daemon=True).start()
        self.reply(b"{}", "application/json")

    def reply(self, body, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # keep the terminal quiet; the page shows progress


def serve(port=8000):
    """Serve the page on this machine only; Ctrl+C stops it."""
    print(f"Open http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
