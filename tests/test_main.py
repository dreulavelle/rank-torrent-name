import pytest

from RTN import parse, RTN
from RTN.extras import title_match, get_lev_ratio, sort_torrents
from RTN.fetch import check_exclude_languages, check_fetch
from RTN.models import ParsedData, SettingsModel, Torrent, DefaultRanking
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
    ("Marvel's Agents of S.H.I.E.L.D.", "marvels agents of shield"),
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
        ("Sprint.2024.S01.COMPLETE.1080p.WEBDL-Rip.h264-EDITH[TGx]", "1234567890123456789012345678901234567890"),
        ("Madame Web 2024 1080p WEBRip 1400MB DD 5.1 x264-GalaxyRG[TGx]", "1234567890123456789012345678901234567891"),
        ("Guardians of the Galaxy Vol. 2 (2017) 720p HDTC x264 MKVTV", "1234567890123456789012345678901234567892"),
        ("Wonder Woman 1984 (2020) [UHDRemux 2160p DoVi P8 Es-DTSHD AC3 En-AC3", "1234567890123456789012345678901234567893"),
        ("ww.Tamilblasters.sbs - 8 Bit Christmas (2021) HQ HDRip - x264 - Telugu (Fan Dub) - 400MB", "1234567890123456789012345678901234567894"),
        ("[SubsPlease] Fairy Tail - 100 Years Quest - 05 (1080p) [1107F3A9].mkv", "1234567890123456789012345678901234567895")
    ]

    torrent_objs = {rtn.rank(torrent, hash) for torrent, hash in torrents}
    sorted_torrents = sort_torrents(torrent_objs)

    expected_order = [
        "1234567890123456789012345678901234567893",  # Wonder Woman 1984 (2020) [UHDRemux 2160p DoVi P8 Es-DTSHD AC3 En-AC3
        "1234567890123456789012345678901234567895",  # [SubsPlease] Fairy Tail - 100 Years Quest - 05 (1080p) [1107F3A9].mkv
        "1234567890123456789012345678901234567891",  # Madame Web 2024 1080p WEBRip 1400MB DD 5.1 x264-GalaxyRG[TGx]
        "1234567890123456789012345678901234567890",  # Sprint.2024.S01.COMPLETE.1080p.WEBDL-Rip.h264-EDITH[TGx]
        "1234567890123456789012345678901234567892",  # Guardians of the Galaxy Vol. 2 (2017) 720p HDTC x264 MKVTV
        "1234567890123456789012345678901234567894"   # ww.Tamilblasters.sbs - 8 Bit Christmas (2021) HQ HDRip - x264 - Telugu (Fan Dub) - 400MB
    ]

    assert list(sorted_torrents.keys()) == expected_order, f"Expected order: {expected_order}, Actual order: {list(sorted_torrents.keys())}"

@pytest.mark.parametrize("raw_title, expected_result", [
    ("The Walking Dead S05E03", True),
    ("The Walking Dead S05E03 [English]", True),
    ("The Walking Dead S05E03 [English] [Spanish]", False)
])
def test_remove_languages(raw_title, expected_result, settings):
    data = parse(raw_title)
    result = check_fetch(data, settings)
    assert result == expected_result, f"Expected result: {expected_result}, Actual result: {result}"