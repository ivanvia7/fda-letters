# fda-letters

Download every FDA warning letter to CSV or JSONL, with the cited CFR rules and U.S.C. sections parsed out.

FDA posts warning letters as web pages, one at a time, with no bulk download.
Quality and regulatory teams read them to see what FDA cites and where:
which 21 CFR 211 sections come up most for drug makers, or what device makers get cited for under part 820.
This tool turns the pages into one table you can filter, count and chart.

## Quick start

```sh
uv tool install git+https://github.com/ivanvia7/fda-letters
fda-letters --out letters.csv
fda-letters --serve
```

The first run fetches every letter into `letters.db` in the current folder.
It sends one request a second, so the first full run takes about 1.5 to 2 hours.
Stop it any time: saved letters stay, and the next run picks up where it stopped.
Later runs fetch only new letters.
A letter page that fda.gov fails to serve is skipped and tried again on the next run.
fda.gov lists letters issued from 2021 on: 3,797 letters on 2026-11-04.
`--serve` serves a page on http://localhost:8000 to fetch, search and export.

## Options

- `--out letters.csv` or `--out letters.jsonl` picks the format.
- `--since 2026-01-01` keeps letters issued on or after that date.
- `--limit 50` stops after 50 new letters.
- `--no-fetch` exports the letters already in `letters.db` without asking fda.gov.

## Output

One row per letter. Columns:

| Column | Example |
|---|---|
| `posted`, `issued`, `closeout` | `2026-11-06` |
| `company`, `url`, `office`, `subject` | from the fda.gov letter list |
| `Product`, `Recipient`, `Delivery Method` | from the letter page |
| `cfr` | `211.22; 211.100; 211.192` cited 21 CFR sections |
| `cfr_parts` | `210; 211` 21 CFR parts cited whole |
| `usc` | `331; 351; 360eee-1` cited 21 U.S.C. sections |

CSV leaves out the letter text. JSONL includes it as `text`.

## How accurate the citations are

The parser is a set of regular expressions in `src/fda_letters/citations.py`.
`tests/test_citation_eval.py` scores it on 30 random letters in `tests/fixtures/eval/`, not the letters the parser was first written against:

| Column | Precision | Recall | Citations in the 30 letters |
|---|---|---|---|
| `cfr` | 100% | 98.8% | 83 |
| `cfr_parts` | 100% | 100% | 42 |
| `usc` | 100% | 100% | 141 |

Read these as upper bounds, not as hand-checked truth.
The labels come from comparing the parser to a looser search and reading by hand every place the two disagree.
A citation both of them miss is not in the labels, and citations both found were not each read.
A code review found 2 part citations both had missed, `(21 CFR, Part 820)` and `[21 CFR 312]`: parts recall was 95% (40 of 42) before the parser learned those spellings.
The bare form `21 CFR 312` is barely in the 30 letters, so it was checked apart: across 708 fetched letters it matched 104 times.
Of 25 picked at random, listed in `tests/fixtures/eval/bare_parts_sample.jsonl`, 23 are clean part citations.
The other 2: the range `21 CFR 1000-1005` gives only part 1000, and the garbled `21 CFR1 .500` gives part 1.
The one `cfr` miss is `CFR 201.66(b)(2)` written without the "21".
Run `uv run python tests/test_citation_eval.py` to print the scores; CI fails if they drop.

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
