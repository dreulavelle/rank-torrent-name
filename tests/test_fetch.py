import pytest

from RTN.fetch import (
    check_fetch,
    check_trash,
    fetch_audio,
    fetch_codec,
    fetch_quality,
    fetch_resolution,
)
from RTN.models import CustomRank, ParsedData, SettingsModel


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
        require=["Horror", "/mario/"],
        exclude=["/japan/", "dubbed"],
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
    # TODO: This test is incomplete.
    data = ParsedData(
        raw_title="The.Lion.King.2019.1080p.BluRay.x264.DTS-HD.MA.7.1-FGT",
        parsed_title="The Lion King",
    )

    assert check_fetch(data, true_fetch_settings) is True
    assert check_fetch(data, false_fetch_settings) is True

    data.raw_title = "Guardians of the Galaxy (CamRip / 2014)"
    assert check_fetch(data, true_fetch_settings) is False
    assert check_fetch(data, false_fetch_settings) is False

    data.raw_title = "Brave.2012.R5.DVDRip.XViD.LiNE-UNiQUE"
    assert check_fetch(data, true_fetch_settings) is False
    assert check_fetch(data, false_fetch_settings) is False

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

    data.is_4k = True # Turn on for purpose of this test
    assert fetch_resolution(data, true_fetch_settings) is True
    assert fetch_resolution(data, false_fetch_settings) is False
    data.is_4k = False # Turn back off for the remainder of tests

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
