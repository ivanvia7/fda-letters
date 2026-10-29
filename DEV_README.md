# Developer notes

## Selectors on fda.gov letter pages

Pick boxes by HTML tag or role, not by class name.

- `dt` and `dt + dd` read the label-value pairs, such as Product and Issuing Office.
- `div[role=main]` holds the letter text.

Why: fda.gov splits the fields across 3 `<dl>` boxes. Only one has a class
(`lcds-description-list--grid`), and it holds 3 of the 5 fields.
Class names are design names, and a restyle silently drops fields.

Use a class only when no tag or role marks the box you need.

## The web page never blocks

`--serve` runs on `ThreadingHTTPServer`, so each request gets its own thread.
A fetch runs in a background thread, and the page asks `/status` once a second.
Search and downloads keep working while a fetch runs.
A second fetch while one runs gets HTTP 409, so two fetches never write to `letters.db` at once.

Keep it that way: never do network or long work inside a request handler.

## The proxy is optional

With no `HTTPS_PROXY`, requests go straight to fda.gov.
Set `HTTPS_PROXY` only when fda.gov blocks your IP or your network needs a proxy.
The CLI and `--serve` both read it from the same client in `letter.py`.

## Commit and branch names

Commit subject: `type(fda-letters): Sentence in the imperative`.

- `type` is one of `feat`, `fix`, `docs`, `test`, `chore`.
- Start the sentence with a capital letter, no period at the end.
- Say what changes for the user: `fix(fda-letters): Stop on HTTP errors, reject bad --out`.
- Never put an issue number or `Closes #N` in a commit; link issues from the PR.

Branch name: `type/short-words`, for example `docs/commit-style`.
