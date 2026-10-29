from fda_letters.citations import cfr_rules, usc_sections


def test_usc_lists():
    assert usc_sections("21 U.S.C. 355(a) and 331(d)") == ["331", "355"]
    assert usc_sections("21 U.S.C. §§ 321, 331, and 352(a)") == ["321", "331", "352"]
    assert usc_sections("21 U.S.C. §§ 331(a) and (bb)") == ["331"]
    assert usc_sections("21 U.S.C. § 360(k), and 21 CFR 807") == ["360"]


def test_cfr_spellings():
    assert cfr_rules("21 CFR 801.3 or 830.3") == ["801.3", "830.3"]
    assert cfr_rules("21 C.F.R. § 1100.1") == ["1100.1"]
    assert cfr_rules("21 CFR part 1.502(a)") == ["1.502"]
    assert cfr_rules("21 CFR1.502") == ["1.502"]
    assert cfr_rules("21 CFR parts 210 and 211") == []
