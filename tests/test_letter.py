from pathlib import Path

from fda_letters.letter import parse_letter

FIXTURE = Path(__file__).parent / "fixtures" / "rohto-733215.html"


def test_parse_rohto_letter():
    letter = parse_letter(FIXTURE.read_text())
    assert letter["Reference #"] == "320-27-06"
    assert letter["Issuing Office"] == "Center for Drug Evaluation and Research (CDER), United States"
    assert letter["Recipient"].startswith("Mr. Kunio Yamada, Chairman")
    assert letter["text"].startswith("Delivery Method:")
