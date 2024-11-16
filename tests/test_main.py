import pytest

from RTN import RTN, parse
from RTN.exceptions import GarbageTorrent
from RTN.extras import get_lev_ratio, sort_torrents, title_match
from RTN.fetch import adult_handler, check_fetch, language_handler, trash_handler
from RTN.models import DefaultRanking, SettingsModel
from RTN.patterns import normalize_title


@pytest.fixture
def settings():
    return SettingsModel()

@pytest.fixture
def ranking():
    return DefaultRanking()


@pytest.mark.parametrize("raw_title, correct_title, expected_match, expected_ratio", [
    ("The Walking Dead", "The Walking Dead", True, 0.85),
    ("The Walking Dead S05E03 720p HDTV x264-ASAP", "The Walking Dead", True, 0.85),
    ("marvels.agents.of.s.h.i.e.l.d.s03.1080p.bluray.x264-shortbrehd[rartv]", "Marvel's Agents of S.H.I.E.L.D.", True, 0.85),
    ("The Walking Dead", "Oppenheimer", False, 0)
])
def test_title_match(raw_title, correct_title, expected_match, expected_ratio):
    data = parse(raw_title)
    match = title_match(correct_title, data.parsed_title)
    ratio = get_lev_ratio(correct_title, data.parsed_title)

    assert match is expected_match, f"Expected match: {expected_match}, Actual match: {match}"
    if expected_ratio != 0:
        assert ratio >= expected_ratio, f"Expected ratio: {expected_ratio}, Actual ratio: {ratio}"
    else:
        assert ratio == expected_ratio, f"Expected ratio: 0, Actual ratio: {ratio}"


@pytest.mark.parametrize("raw_title, expected_normalized_title", [
    ("The Walking Dead", "the walking dead"),
    ("Marvel's Agents of S.H.I.E.L.D.", "marvels agents of s h i e l d"),
    ("The Walking Dead S05E03 720p HDTV x264-ASAP", "the walking dead"),
    ("фуриоса: хроники безумного макса", "фуриоса хроники безумного макса"),
    ("200% Wolf", "200 wolf")
])
def test_normalize_title(raw_title, expected_normalized_title):
    data = parse(raw_title)
    normalized_title = normalize_title(data.parsed_title)
    assert normalized_title == expected_normalized_title, f"Expected normalized title: '{expected_normalized_title}', Actual normalized title: '{normalized_title}'"


def test_sort_torrents(settings, ranking):
    rtn = RTN(settings, ranking)

    torrents = [
        ("Sprint.2024.S01.COMPLETE.1080p.WEBDL.h264-EDITH[TGx]", "1234567890123456789012345678901234567890"),
        ("Madame Web 2024 1080p WEBRip DD 5.1 x264-GalaxyRG[TGx]", "1234567890123456789012345678901234567891"),
        ("Guardians of the Galaxy Vol. 2 (2017) 720p x264 MKVTV", "1234567890123456789012345678901234567892"),
        ("Wonder Woman 1984 (2020) [1440p DoVi P8 DTSHD AC3 En-AC3", "1234567890123456789012345678901234567893"),
        ("8 Bit Christmas (2021) - x264 - Telugu (Fan Dub)", "1234567890123456789012345678901234567894"),
        ("[SubsPlease] Fairy Tail - 100 Years Quest - 05 (1080p) [1107F3A9].mkv", "1234567890123456789012345678901234567895")
    ]

    torrent_objs = {rtn.rank(torrent, hash) for torrent, hash in torrents}
    sorted_torrents = sort_torrents(torrent_objs)

    expected_order = [
        "1234567890123456789012345678901234567893",  # Wonder Woman 1984 (2020) [UHDRemux 2160p DoVi P8 Es-DTSHD AC3 En-AC3
        "1234567890123456789012345678901234567890",  # Sprint.2024.S01.COMPLETE.1080p.WEBDL-Rip.h264-EDITH[TGx]
        "1234567890123456789012345678901234567891",  # Madame Web 2024 1080p WEBRip 1400MB DD 5.1 x264-GalaxyRG[TGx]
        "1234567890123456789012345678901234567895",  # [SubsPlease] Fairy Tail - 100 Years Quest - 05 (1080p) [1107F3A9].mkv
        "1234567890123456789012345678901234567892",  # Guardians of the Galaxy Vol. 2 (2017) 720p HDTC x264 MKVTV
        "1234567890123456789012345678901234567894"   # ww.Tamilblasters.sbs - 8 Bit Christmas (2021) HQ HDRip - x264 - Telugu (Fan Dub) - 400MB
    ]

    assert list(sorted_torrents.keys()) == expected_order, f"Expected order: {expected_order}, Actual order: {list(sorted_torrents.keys())}"


@pytest.mark.parametrize("raw_title, expected_exclude", [
    ("The Walking Dead S05E03", False),
    ("The Walking Dead S05E03 [English]", False),
    ("The Walking Dead S05E03 [English] [Spanish]", True)
])
def test_exclude_languages(raw_title, settings, expected_exclude):
    data = parse(raw_title)
    failed_keys = set()
    exclude_languages_result = language_handler(data, settings, failed_keys)
    assert exclude_languages_result == expected_exclude, f"Expected exclude language result: {expected_exclude}, Actual result: {exclude_languages_result}"


@pytest.mark.parametrize("raw_title, expected_trash", [
    ("Deadpool & Wolverine (2024) Eng 1080p V3 HDTS AAC ESub mkv", True),
    ("Deadpool & Wolverine (2024) HDTS mkv", True), 
    ("Deadpool&Wolverine 2024-TeleSync mkv", True),
    ("Deadpool & Wolverine (2024) 1080p TELESYNC V4 [Hindi + English] AAC Dual Audio ESub x264 AVC - 2700MB - [PotonMovies]", True),
    ("Deadpool.And.Wolverine.2024.2160p.HDR.Multi.Audio.TELESYNC.HEVC.COLLECTiVE", True),
    ("The Walking Dead S05E03 720p x264-ASAP", False)
])
def test_trash_handler(settings, raw_title, expected_trash):
    """Test that trash detection works correctly"""
    data = parse(raw_title)
    failed_keys = set()

    trash_result = trash_handler(data, settings, failed_keys)
    assert trash_result == expected_trash, f"Expected trash result: {expected_trash}, got: {trash_result}"

    # If it's trash, check_fetch should raise GarbageTorrent
    if expected_trash:
        with pytest.raises(GarbageTorrent):
            check_fetch(data, settings, failed_keys)
    else:
        # Not trash, so check_fetch should succeed
        assert check_fetch(data, settings, failed_keys)


@pytest.mark.parametrize("raw_title, expected_result, expected_seasons, expected_episodes", [
    ("Mad.Max.Fury.Road.2015.1080p.BluRay.DDP5.1.x265.10bit-GalaxyRG265[TGx]", "movie", [], []),
    ("Furiosa A Mad Max Saga (2024) [1080p] [WEBRip] [x265] [10bit] [5.1] [YTS.MX]", "movie", [], []),
    ("The Walking Dead S05E03 720p x264-ASAP", "show", [5], [3]),
])
def test_type_check_on_item(raw_title, expected_result, expected_seasons, expected_episodes):
    data = parse(raw_title)
    assert data.type == expected_result, f"Expected type check result: {expected_result}, Actual result: {data.type}"
    assert data.seasons == expected_seasons, f"Expected seasons check result: {expected_seasons}, Actual result: {data.seasons}"
    assert data.episodes == expected_episodes, f"Expected episodes check result: {expected_episodes}, Actual result: {data.episodes}"


@pytest.mark.parametrize("raw_title, expected_adult", [
    ("Deadpool & Wolverine (2024) Eng 1080p V3 HDTS AAC ESub xvideos mkv", True),
    ("The Walking Dead S05E03 720p x264-ASAP vrporn", True),
    ("The Walking Dead S05E03 720p x264-ASAP", False)
])
def test_adult_handler(settings, raw_title, expected_adult):
    data = parse(raw_title)
    failed_keys = set()
    adult_result = adult_handler(data, settings, failed_keys)
    assert adult_result == expected_adult, f"Expected adult result: {expected_adult}, got: {adult_result}"
