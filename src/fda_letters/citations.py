import re

# One rule: digits, a dot, digits, then any "(a)" parts. Lists join like USC below.
RULE = r"\d+\.\d+(?:\(\w+\))*"
JOIN = r"(?:,? and |,? or |, )"
# "21 CFR", "21CFR" or "21 C.F.R."
CFR_TITLE = r"21 ?C\.?F\.?R\.? ?"

# Title, then an optional "§ ", "§§ " or "part " before the rules.
CFR = re.compile(rf"{CFR_TITLE}(?:§§? |[Pp]art )?({RULE}(?:{JOIN}{RULE})*)")

# "21 CFR part 211" or "parts 210 and 211": whole parts, no section after them,
# and not the "21" of a next "21 CFR".
PART = r"\d+\b(?!\.\d| ?C\.?F\.?R)"
CFR_PART = re.compile(rf"{CFR_TITLE}[Pp]arts? ({PART}(?:{JOIN}{PART})*)")

# One section: 3 digits, optional letters, an optional "-1" as in 360eee-1,
# then any "(a)", "(j)(2)" parts.
SECTION = r"\d{3}[a-z]*(?:-\d+)?(?:\(\w+\))*"

# "21 U.S.C.", optional "§ " or "§§ ", then sections joined by ", ", " and ", " or ".
USC = re.compile(rf"21 U\.S\.C\. (?:§§? )?({SECTION}(?:{JOIN}{SECTION})*)")
PARENS = re.compile(r"\(\w+\)")


def normalize(text: str) -> str:
    # fda.gov pages put non-breaking spaces after "§" and in "21 U.S.C.".
    return text.replace("\xa0", " ")


def cfr_rules(text: str) -> list[str]:
    """Return the unique 21 CFR section numbers cited in a letter, sorted."""
    found = set()
    for chunk in CFR.findall(normalize(text)):
        found.update(re.findall(r"\d+\.\d+", chunk))
    # By number, so 211.22 sorts before 211.194.
    return sorted(found, key=lambda rule: [int(n) for n in rule.split(".")])


def cfr_parts(text: str) -> list[str]:
    """Return the unique 21 CFR parts cited whole, as in "parts 210 and 211"."""
    found = set()
    for chunk in CFR_PART.findall(normalize(text)):
        found.update(re.findall(r"\d+", chunk))
    return sorted(found, key=int)


def usc_sections(text: str) -> list[str]:
    """Return the unique 21 U.S.C. section numbers cited in a letter, sorted."""
    found = set()
    for chunk in USC.findall(normalize(text)):
        found.update(re.findall(r"\d+[a-z]*(?:-\d+)?", PARENS.sub("", chunk)))
    return sorted(found)


def citations(text: str) -> dict[str, str]:
    """The citation columns for one letter, each joined with "; "."""
    return {
        "cfr": "; ".join(cfr_rules(text)),
        "cfr_parts": "; ".join(cfr_parts(text)),
        "usc": "; ".join(usc_sections(text)),
    }
