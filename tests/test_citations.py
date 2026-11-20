from fda_letters.citations import cfr_parts, cfr_rules, usc_sections


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


def test_cfr_number_order():
    assert cfr_rules("21 CFR 211.194, 211.22 and 1100.1") == [
        "211.22",
        "211.194",
        "1100.1",
    ]


def test_real_letter_spellings():
    # Seen on fda.gov: non-breaking space after "§", no space in "21CFR", "-1" sections.
    assert usc_sections("(21 U.S.C.\xa0§\xa0321(rr))") == ["321"]
    assert cfr_rules("as required by 21CFR 820.90(a).") == ["820.90"]
    assert usc_sections("[21 U.S.C. § 360eee-1]") == ["360eee-1"]
    assert usc_sections("21 U.S.C. 360bbb-3(b) and 355") == ["355", "360bbb-3"]


def test_cfr_parts():
    assert cfr_parts("21 CFR parts 210 and 211.") == ["210", "211"]
    assert cfr_parts("21 CFR part 1, subpart L") == ["1"]
    assert cfr_parts("21 CFR Part 806 and 21 CFR part 1271") == ["806", "1271"]
    assert cfr_parts("21 CFR part 1.502(a)") == []


def test_review_round_spellings():
    # A range keeps only its first section; "-1" belongs to lettered sections only.
    assert usc_sections("21 U.S.C. 351-360") == ["351"]
    assert usc_sections("21 U.S.C. §§ 331-333") == ["331"]
    # No space after "§".
    assert cfr_rules("21 CFR §211.22") == ["211.22"]
    assert usc_sections("21 U.S.C. §331(a)") == ["331"]
    # Parts after a comma, and a bare part number.
    assert cfr_parts("(21 CFR, Part 820)") == ["820"]
    assert cfr_parts("part 312 [21 CFR 312]") == ["312"]
    assert cfr_parts("21 CFR 211.22") == []
    # A paragraph right after the number is a mangled section, not a whole part.
    assert cfr_parts("21 CFR 42(c)(10)(iv)") == []
    assert cfr_parts("21 CFR parts 210 and 211 (CGMP)") == ["210", "211"]
