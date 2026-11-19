"""Score the citation parser against hand-checked labels for 30 random letters.

Labels: the parser's output and a looser search were compared on every letter,
and each place they disagreed was read by hand. Citations both found were not
each read, so precision here is an upper bound. Run as a script to print scores:

    uv run python tests/test_citation_eval.py
"""

import json
from pathlib import Path
from typing import Any

from fda_letters.citations import cfr_parts, cfr_rules, usc_sections

EVAL = Path(__file__).parent / "fixtures" / "eval"
PARSERS = {"cfr": cfr_rules, "cfr_parts": cfr_parts, "usc": usc_sections}


def load(name: str) -> dict[str, dict[str, Any]]:
    lines = (EVAL / name).read_text(encoding="utf-8").splitlines()
    return {row["url"]: row for row in map(json.loads, lines)}


def score() -> dict[str, dict[str, float]]:
    """Precision and recall per column, counted over every (letter, citation) pair."""
    letters, labels = load("letters.jsonl"), load("labels.jsonl")
    scores = {}
    for column, parse in PARSERS.items():
        hits = found = expected = 0
        for url, letter in letters.items():
            got, want = set(parse(letter["text"])), set(labels[url][column])
            hits += len(got & want)
            found += len(got)
            expected += len(want)
        scores[column] = {
            "precision": hits / found,
            "recall": hits / expected,
            "citations": expected,
        }
    return scores


def test_citation_scores():
    # Floors at the scores measured on 2026-11-20; a regex change must not drop them.
    scores = score()
    for column in PARSERS:
        assert scores[column]["precision"] == 1.0
    assert scores["cfr"]["recall"] >= 0.98
    assert scores["cfr_parts"]["recall"] == 1.0
    assert scores["usc"]["recall"] == 1.0


if __name__ == "__main__":
    print(f"{len(load('letters.jsonl'))} letters")
    for column, s in score().items():
        print(
            f"{column:10} precision {s['precision']:.1%}  recall {s['recall']:.1%}"
            f"  ({s['citations']:.0f} citations)"
        )
