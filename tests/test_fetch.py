import pytest

# from hypothesis import HealthCheck, given, settings
# from hypothesis import strategies as st
from RTN.fetch import (
    check_exclude,
    check_fetch,
    check_required,
    check_trash,
    fetch_audio,
    fetch_codec,
    fetch_other,
    fetch_quality,
    fetch_resolution,
)
from RTN.models import CustomRank, ParsedData, SettingsModel

# @st.composite
# def custom_rank(draw, fetch_value=st.booleans()):  # noqa: B008
#     rank = draw(st.integers(min_value=-100, max_value=100))
#     fetch = draw(fetch_value)
#     return CustomRank(enable=True, fetch=fetch, rank=rank)

# # Strategy to generate SettingsModel objects with variable fetch settings for testing
# @st.composite
# def generate_settings(draw):
#     custom_ranks = {
#         "uhd": draw(custom_rank()),
#         "fhd": draw(custom_rank()),
#         "hd": draw(custom_rank()),
#         "sd": draw(custom_rank()),
#         "bluray": draw(custom_rank()),
#         "hdr": draw(custom_rank()),
#         "hdr10": draw(custom_rank()),
#         "dolby_video": draw(custom_rank()),
#         "dts_x": draw(custom_rank()),
#         "dts_hd": draw(custom_rank()),
#         "dts_hd_ma": draw(custom_rank()),
#         "atmos": draw(custom_rank()),
#         "truehd": draw(custom_rank()),
#         "ddplus": draw(custom_rank()),
#         "ac3": draw(custom_rank()),
#         "aac": draw(custom_rank()),
#         "remux": draw(custom_rank()),
#         "webdl": draw(custom_rank()),
#         "repack": draw(custom_rank()),
#         "proper": draw(custom_rank()),
#         "dubbed": draw(custom_rank()),
#         "subbed": draw(custom_rank()),
#         "av1": draw(custom_rank()),
#     }
#     return SettingsModel(custom_ranks=custom_ranks)


@pytest.fixture
def true_fetch_settings():
    return SettingsModel(
        require=[],
        exclude=[],
        custom_ranks={
            "uhd": CustomRank(rank=100, fetch=True),
            "fhd": CustomRank(rank=50, fetch=True),
            "hd": CustomRank(rank=20, fetch=True),
            "sd": CustomRank(rank=10, fetch=True),
            "bluray": CustomRank(rank=10, fetch=True),
            "hdr": CustomRank(rank=10, fetch=True),
            "hdr10": CustomRank(rank=10, fetch=True),
            "dolby_video": CustomRank(rank=10, fetch=True),
            "dts_x": CustomRank(rank=10, fetch=True),
            "dts_hd": CustomRank(rank=10, fetch=True),
            "dts_hd_ma": CustomRank(rank=10, fetch=True),
            "atmos": CustomRank(rank=10, fetch=True),
            "truehd": CustomRank(rank=10, fetch=True),
            "ddplus": CustomRank(rank=10, fetch=True),
            "ac3": CustomRank(rank=10, fetch=True),
            "aac": CustomRank(rank=10, fetch=True),
            "remux": CustomRank(rank=10, fetch=True),
            "webdl": CustomRank(rank=10, fetch=True),
            "repack": CustomRank(rank=10, fetch=True),
            "proper": CustomRank(rank=10, fetch=True),
            "dubbed": CustomRank(rank=10, fetch=True),
            "subbed": CustomRank(rank=10, fetch=True),
            "av1": CustomRank(rank=10, fetch=True),
        },
    )

@pytest.fixture
def false_fetch_settings():
    return SettingsModel(
        require=[],
        exclude=[],
        custom_ranks={
            "uhd": CustomRank(rank=100, fetch=False),
            "fhd": CustomRank(rank=50, fetch=False),
            "hd": CustomRank(rank=20, fetch=False),
            "sd": CustomRank(rank=10, fetch=False),
            "bluray": CustomRank(rank=10, fetch=False),
            "hdr": CustomRank(rank=10, fetch=False),
            "hdr10": CustomRank(rank=10, fetch=False),
            "dolby_video": CustomRank(rank=10, fetch=False),
            "dts_x": CustomRank(rank=10, fetch=False),
            "dts_hd": CustomRank(rank=10, fetch=False),
            "dts_hd_ma": CustomRank(rank=10, fetch=False),
            "atmos": CustomRank(rank=10, fetch=False),
            "truehd": CustomRank(rank=10, fetch=False),
            "ddplus": CustomRank(rank=10, fetch=False),
            "ac3": CustomRank(rank=10, fetch=False),
            "aac": CustomRank(rank=10, fetch=False),
            "remux": CustomRank(rank=10, fetch=False),
            "webdl": CustomRank(rank=10, fetch=False),
            "repack": CustomRank(rank=10, fetch=False),
            "proper": CustomRank(rank=10, fetch=False),
            "dubbed": CustomRank(rank=10, fetch=False),
            "subbed": CustomRank(rank=10, fetch=False),
            "av1": CustomRank(rank=10, fetch=False),
        },
    )


def test_check_if_string_is_trash():
    # True means the string is unwanted, and won't be fetched.
    test_cases = [
        ("Mission.Impossible.1996.Custom.Audio.1080p.PL-Spedboy", False),
        ("Casino.1995.MULTi.REMUX.2160p.UHD.Blu-ray.HDR.HEVC.DTS-X7.1-DENDA", False),
        ("Guardians of the Galaxy (CamRip / 2014)", True),  # CamRip
        ("Brave.2012.R5.DVDRip.XViD.LiNE-UNiQUE", True),    # R5, LiNE
        ("The.Lion.King.2019.1080p.BluRay.x264.DTS-HD.MA.7.1-FGT", False),
        ("The Great Gatsby 2013 1080p BluRay x264 AAC - Ozlem", False),
    ]
    for test_string, expected in test_cases:
        assert check_trash(test_string) == expected

    with pytest.raises(TypeError):
        assert check_trash(123) # type: ignore


def test_check_fetch(true_fetch_settings, false_fetch_settings):
    data = ParsedData(
        raw_title="The.Lion.King.2019.1080p.BluRay.x264.DTS-HD.MA.7.1-FGT",
        parsed_title="The Lion King",
    )

    assert check_fetch(data, true_fetch_settings) is True
    assert check_fetch(data, false_fetch_settings) is True

    data.raw_title = "Guardians of the Galaxy (2014)"
    assert check_fetch(data, true_fetch_settings) is True
    assert check_fetch(data, false_fetch_settings) is True, "Nothing in the title is excluded, so it should return True"


    data.raw_title = "The Great Gatsby 2013 1080p BluRay x264 AAC - Ozlem"
    assert check_fetch(data, true_fetch_settings) is True
    assert check_fetch(data, false_fetch_settings) is True


def test_fetch_audio(true_fetch_settings, false_fetch_settings):
    data = ParsedData(
        raw_title="The.Lion.King.2019.1080p.BluRay.x264.DTS-HD.MA.7.1-FGT",
        parsed_title="The Lion King",
    )

    data.audio = ["Dolby TrueHD"]
    assert fetch_audio(data, true_fetch_settings) is True
    assert fetch_audio(data, false_fetch_settings) is False

    data.audio = ["Dolby Atmos"]
    assert fetch_audio(data, true_fetch_settings) is True
    assert fetch_audio(data, false_fetch_settings) is False

    data.audio = ["Dolby Digital"] # AC3
    assert fetch_audio(data, true_fetch_settings) is True
    assert fetch_audio(data, false_fetch_settings) is False

    data.audio = ["Dolby Digital EX"]
    assert fetch_audio(data, true_fetch_settings) is True
    assert fetch_audio(data, false_fetch_settings) is False

    data.audio = ["Dolby Digital Plus"]
    assert fetch_audio(data, true_fetch_settings) is True
    assert fetch_audio(data, false_fetch_settings) is False

    data.audio = ["DTS-HD MA"]
    assert fetch_audio(data, true_fetch_settings) is True
    assert fetch_audio(data, false_fetch_settings) is False

    data.audio = ["DTS"]
    assert fetch_audio(data, true_fetch_settings) is True
    assert fetch_audio(data, false_fetch_settings) is False

    data.audio = ["AAC"]
    assert fetch_audio(data, true_fetch_settings) is True
    assert fetch_audio(data, false_fetch_settings) is False

    data.audio = ["FLAC"] # Not in settings but default is True
    assert fetch_audio(data, true_fetch_settings) is True
    assert fetch_audio(data, false_fetch_settings) is True


def test_fetch_resolution(true_fetch_settings, false_fetch_settings):
    data = ParsedData(
        raw_title="The.Lion.King.2019.1080p.BluRay.x264.DTS-HD.MA.7.1-FGT",
        parsed_title="The Lion King",
    )

    data.resolution = ["4K"]
    assert fetch_resolution(data, true_fetch_settings) is True
    assert fetch_resolution(data, false_fetch_settings) is False

    data.resolution = ["2160p"]
    assert fetch_resolution(data, true_fetch_settings) is True
    assert fetch_resolution(data, false_fetch_settings) is False

    data.resolution = ["1440p"]
    assert fetch_resolution(data, true_fetch_settings) is True
    assert fetch_resolution(data, false_fetch_settings) is False
    
    data.resolution = ["1080p"]
    assert fetch_resolution(data, true_fetch_settings) is True
    assert fetch_resolution(data, false_fetch_settings) is False

    data.resolution = ["720p"]
    assert fetch_resolution(data, true_fetch_settings) is True
    assert fetch_resolution(data, false_fetch_settings) is False

    data.resolution = ["576p"]
    assert fetch_resolution(data, true_fetch_settings) is True
    assert fetch_resolution(data, false_fetch_settings) is False

    data.resolution = ["480p"]
    assert fetch_resolution(data, true_fetch_settings) is True
    assert fetch_resolution(data, false_fetch_settings) is False

    data.resolution = ["360p"] # Not in settings but default is True
    assert fetch_resolution(data, true_fetch_settings) is True
    assert fetch_resolution(data, false_fetch_settings) is True


def test_fetch_codec(true_fetch_settings, false_fetch_settings):
    data = ParsedData(
        raw_title="The.Lion.King.2019.1080p.BluRay.x264.DTS-HD.MA.7.1-FGT",
        parsed_title="The Lion King",
    )

    data.codec = ["x264"] # TODO: Not in settings but default is True
    assert fetch_codec(data, true_fetch_settings) is True
    assert fetch_codec(data, false_fetch_settings) is True

    data.codec = ["x265"] # TODO: Not in settings but default is True
    assert fetch_codec(data, true_fetch_settings) is True
    assert fetch_codec(data, false_fetch_settings) is True

    data.codec = ["AV1"]
    assert fetch_codec(data, true_fetch_settings) is True
    assert fetch_codec(data, false_fetch_settings) is False

    data.codec = ["VP9"] # Not in settings but default is True
    assert fetch_codec(data, true_fetch_settings) is True
    assert fetch_codec(data, false_fetch_settings) is True


def test_fetch_quality(true_fetch_settings, false_fetch_settings):
    data = ParsedData(
        raw_title="The.Lion.King.2019.1080p.BluRay.x264.DTS-HD.MA.7.1-FGT",
        parsed_title="The Lion King",
    )

    data.quality = ["WEB-DL"]
    assert fetch_quality(data, true_fetch_settings) is True
    assert fetch_quality(data, false_fetch_settings) is False

    data.remux = True
    assert fetch_quality(data, true_fetch_settings) is True
    assert fetch_quality(data, false_fetch_settings) is False
    data.remux = False


def test_fetch_other(true_fetch_settings, false_fetch_settings):
    data = ParsedData(
        raw_title="The.Lion.King.2019.1080p.BluRay.x264.DTS-HD.MA.7.1-FGT",
        parsed_title="The Lion King",
    )

    data.proper = True
    assert fetch_other(data, true_fetch_settings) is True
    assert check_fetch(data, false_fetch_settings) is False

    data.proper = False
    data.repack = True
    assert fetch_other(data, true_fetch_settings) is True
    assert check_fetch(data, false_fetch_settings) is False

    data.proper = False
    data.repack = False
    assert fetch_other(data, true_fetch_settings) is True
    assert check_fetch(data, false_fetch_settings) is True, "We return True because the default is True"


def test_explicit_check_required():
    settings = SettingsModel(
        require=["4K", "/1080p/i", "/awesome/", "SPIDER|Traffic|/compressed/"],  # "/4K/" is case-sensitive, "/1080p/i" is case-insensitive
    )

    data = ParsedData(
        raw_title="This is a 4k video",
        parsed_title="4k Video",
    )
    assert check_required(data, settings) is True, "4K should match as case-insensitive on required on default behavior"

    data.raw_title = "This is a 1080P video"
    assert check_required(data, settings) is True, "/1080p/i should match as case-insensitive on required"
    assert check_fetch(data, settings) is True, "Should be True because check_required is True"

    data.raw_title = "Awesome BluRay Release"
    assert check_required(data, settings) is False, "Should not match because 'awesome' is required as case-sensitive"

    data.raw_title = "Exclusive HDR10+ Content"
    assert check_required(data, settings) is False, "Should fail because it's not in the list of required patterns"

    data.raw_title = "House MD All Seasons (1-8) 720p Ultra-Compressed"
    assert check_required(data, settings) is False, "Should not match because 'compressed' is case-sensitive"

    data.raw_title = "House MD All Seasons (1-8) 720p spider"
    assert check_required(data, settings) is True, "Should match because 'spider' is not case-sensitive and required"

    settings.require = []
    data.raw_title = "Exclusive HDR10+ Content"
    assert check_required(data, settings) is False, "Should fail because there are no required patterns, therefore it should return False"


def test_explicit_check_excluded():
    settings = SettingsModel(
        exclude=["4K", "/japan/", "SPIDER|Traffic|/compressed/", "brazil", "/ca[M]/i", "S\\d{2}"], 
    )

    data = ParsedData(
        raw_title="This is a 4k video",
        parsed_title="4k Video",
    )

    assert check_exclude(data, settings) is True, "Case-insensitive should match because '4K' is excluded"

    data.raw_title = "This is a BraZil video"
    assert check_exclude(data, settings) is True, "Case-insensitive should match because 'brazil' is excluded"
    assert check_fetch(data, settings) is False, "Should be False because check_exclude is True"

    data.raw_title = "Low Quality CAM"
    assert check_exclude(data, settings) is True, "Should match because 'CAM' is excluded - case-insensitive"
    assert check_fetch(data, settings) is False, "Should be False because check_exclude is True"

    data.raw_title = "Exclusive HDR10+ Content"
    assert check_exclude(data, settings) is False, "Should fail because it's not in the list of excluded patterns"

    data.raw_title = "Game.of.Thrones.S08E01.1080p.WEB-DL.DDP5.1.H.264-GoT"
    assert check_exclude(data, settings) is True, "Should match because 'S08' is excluded"

    data.raw_title = "Exclusive HDR10+ Content"
    assert check_exclude(data, settings) is False, "Should fail because there are no excluded patterns, therefore it should return False"

    settings = SettingsModel(
        exclude=["S\d{2}"],  # type: ignore
    )

    data.raw_title = "Game.of.Thrones.S08E01.1080p.WEB-DL.DDP5.1.H.264-GoT"
    assert check_exclude(data, settings) is True, "We should support non-escaped characters as valid regex patterns"

    settings = SettingsModel(
        exclude=["S\\d{2}"], 
    )

    data.raw_title = "Game.of.Thrones.S08E01.1080p.WEB-DL.DDP5.1.H.264-GoT"
    assert check_exclude(data, settings) is True, "We should support escaped characters as valid regex patterns"