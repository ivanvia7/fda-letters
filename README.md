# fda-letters

Download every FDA warning letter to CSV or JSONL, with the cited CFR rules and U.S.C. sections parsed out.

## Quick start

```sh
uv tool install git+https://github.com/ivanvia7/fda-letters
fda-letters --out letters.csv
fda-letters --serve
```

The first run fetches every letter into `letters.db` in the current folder.
Later runs fetch only new letters.
`--serve` serves a page on http://localhost:8000 to fetch, search and export.

## Options

- `--out letters.csv` or `--out letters.jsonl` picks the format.
- `--since 2026-01-01` keeps letters issued on or after that date.
- `--limit 50` stops after 50 new letters.

## Web page

Run `fda-letters --serve` and open http://localhost:8000.
The page runs on your machine only. Ctrl+C in the terminal stops it.

Fetch new letters:

- **Issued since** sets the earliest issue date. Leave it empty for every letter.
- **Last 30 days**, **Last year** and **Any date** fill that date for you.
- **Max new letters** stops the fetch after that many letters. Leave it empty for no limit.
- **Fetch new letters** starts the fetch. A progress bar counts the letters as they arrive.
- When the fetch ends, the page links `letters.csv` and `letters.jsonl` for the chosen dates.

Saved letters:

- The table shows the newest 50 letters already in `letters.db`.
- The search box filters by company or subject as you type.
- Each company name links to the letter on fda.gov.
- **CSV** and **JSON** download every saved letter.

## Proxy

Set `HTTPS_PROXY` to send requests through any HTTP proxy:

```sh
HTTPS_PROXY=http://user:pass@host:port fda-letters --out letters.csv
```

## License

MIT
