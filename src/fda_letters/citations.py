import re

# One rule: digits, a dot, digits, then any "(a)" parts. Lists join like USC below.
RULE = r"\d+\.\d+(?:\(\w+\))*"
# "21 CFR" or "21 C.F.R.", then an optional "§ ", "§§ " or "part " before the rules.
CFR = re.compile(rf"21 C\.?F\.?R\.? ?(?:§§? |[Pp]art )?({RULE}(?:(?:,? and |,? or |, ){RULE})*)")
# One section: 3 digits, optional letters, then any "(a)", "(j)(2)" parts.
SECTION = r"\d{3}[a-z]*(?:\(\w+\))*"
# "21 U.S.C.", optional "§ " or "§§ ", then sections joined by ", ", " and ", " or ".
USC = re.compile(
    rf"21 U\.S\.C\. (?:§§? )?({SECTION}(?:(?:,? and |,? or |, ){SECTION})*)"
)
PARENS = re.compile(r"\(\w+\)")


def cfr_rules(text):
    """Return the unique 21 CFR section numbers cited in a letter, sorted."""
    found = set()
    for chunk in CFR.findall(text):
        found.update(re.findall(r"\d+\.\d+", chunk))
    return sorted(found)


def usc_sections(text):
    """Return the unique 21 U.S.C. section numbers cited in a letter, sorted."""
    found = set()
    for chunk in USC.findall(text):
        found.update(re.findall(r"\d+[a-z]*", PARENS.sub("", chunk)))
    return sorted(found)


if __name__ == "__main__":
    from fda_letters.letter import parse_letter

    html = open("tests/fixtures/rohto-733215.html", encoding="utf-8").read()
    text = parse_letter(html)["text"]
    print(cfr_rules(text))
    print(usc_sections(text))
