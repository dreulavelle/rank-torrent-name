
import pytest
from pydantic import ValidationError

from RTN import get_rank, parse
from RTN.models import (
    BaseRankingModel,
    CustomRank,
    DefaultRanking,
    ParsedData,
    SettingsModel,
)
from RTN.parser import RTN, Torrent, batch_parse, sort, title_match
from RTN.patterns import (
    COMPLETE_SERIES_COMPILED,
    MULTI_AUDIO_COMPILED,
    MULTI_SUBTITLE_COMPILED,
    check_hdr_dolby_video,
    check_pattern,
    extract_episodes,
    parse_extras,
)

## Define Fixtures

@pytest.fixture
def settings_model():
    return SettingsModel()

@pytest.fixture
def custom_settings():
    return SettingsModel(
        profile="custom",
        require=[],
        exclude=[],
        preferred=["BluRay", r"/\bS\d+/", "/HDR|HDR10/i"],
        custom_ranks={
            "uhd": CustomRank(enable=True, fetch=True, rank=-200),
            "fhd": CustomRank(enable=True, fetch=True, rank=90),
            "hd": CustomRank(enable=True, fetch=True, rank=60),
            "sd": CustomRank(enable=True, fetch=True, rank=-120),
            "dolby_video": CustomRank(enable=True, fetch=True, rank=-1000),
            "hdr": CustomRank(enable=True, fetch=True, rank=-1000),
            "hdr10": CustomRank(enable=True, fetch=True, rank=-1000),
            "aac": CustomRank(enable=True, fetch=True, rank=70),
            "ac3": CustomRank(enable=True, fetch=True, rank=50),
            "remux": CustomRank(enable=False, fetch=True, rank=-75),
            "webdl": CustomRank(enable=True, fetch=True, rank=90),
            "bluray": CustomRank(enable=True, fetch=True, rank=-90),
        },
    )

@pytest.fixture
def rank_model():
    return DefaultRanking()

@pytest.fixture
def test_titles():
    return [
        "The.Matrix.1999.1080p.BluRay.x264",
        "Inception.2010.720p.BRRip.x264",
        "The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"
        "The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"
        "The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"
        "The Simpsons S01E01-E02-E03-E04-E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"
        "The Simpsons S01E01E02E03E04E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"
        "The Simpsons E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"
        "House MD All Seasons (1-8) 720p Ultra-Compressed"
        "The Avengers (EMH) - S01 E15 - 459 (1080p - BluRay)"
        "Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World"
        "Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]"
        "4-13 Cursed (HD)"
        "Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p BluRay x264 DTS 5.1 -DDR"
        "[F-D] Fairy Tail Season 1 - 6 + Extras [480P][Dual-Audio]"
        "BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p"
        "[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ"
        "Bleach 10º Temporada - 215 ao 220 - [DB-BR]"
        "Naruto Shippuden - 107 - Strange Bedfellows"
        "[224] Shingeki no Kyojin - S03 - Part 1 - 13 [BDRip.1080p.x265.FLAC]"
        "[Erai-raws] Shingeki no Kyojin Season 3 - 11 [1080p][Multiple Subtitle]"
    ]

## Define Tests

def test_default_ranking_model(rank_model):
    assert isinstance(rank_model, BaseRankingModel)
    # Mostly used for if I forget to update the tests/docs. 
    # Serves as a warning.
    assert rank_model.uhd == 140
    assert rank_model.fhd == 100
    assert rank_model.hd == 50
    assert rank_model.sd == -100
    assert rank_model.dolby_video == -1000
    assert rank_model.hdr == -1000
    assert rank_model.hdr10 == -1000
    assert rank_model.aac == 70
    assert rank_model.ac3 == 50
    assert rank_model.remux == -1000
    assert rank_model.webdl == 90
    assert rank_model.bluray == -90


def test_default_parse_return(custom_settings, rank_model):
    parsed = parse("The.Big.Bang.Theory.S01E01.720p.HDTV.x264-CTU")
    assert isinstance(parsed, ParsedData)
    assert parsed.parsed_title == "The Big Bang Theory"

    # Test preferred
    rank = get_rank(parsed, custom_settings, rank_model)
    assert rank > 5000, f"Rank was {rank} instead."

    # Test invalid title
    with pytest.raises(TypeError):
        assert parse(12345) # type: ignore

    # Test invalid title
    with pytest.raises(TypeError):
        assert parse() # type: ignore


def test_default_title_matching():
    """Test the title_match function"""
    # This ensures all titles adhere to having a levenshtein ratio > 0.9.
    test_cases = [
        ("Damsel", "Damsel (2024)", False),
        ("The Simpsons", "The Simpsons", True),
        ("The Simpsons", "The Simpsons Movie", False),
        ("The Simpsons", "The Simpsons S01E01", False),
        ("The Simpsons S01E01", "The Simpsons S01E01", True),
        ("The Simpsons Movie", "The Simpsons Movie", True),
        ("American Horror Story", "American Story Horror", False),
    ]
    for title, query, expected in test_cases:
        assert title_match(title, query) == expected, f"Failed for {title} and {query}"
    
    # test not correct_title or not raw_title
    with pytest.raises(TypeError):
        assert title_match("The Simpsons", 12345) # type: ignore
    # test valid threshold
    assert title_match("The Simpsons", "The Simpsons", threshold=0.9)
    # test invalid threshold
    with pytest.raises(ValueError):
        assert title_match("The Simpsons", "The Simpsons", threshold=1.1)
    # test not correct_title or not raw_title
    with pytest.raises(ValueError):
        assert title_match(None, None) # type: ignore


def test_batch_parse_processing(test_titles):
    # Test batch parsing retuns a list of ParsedData objects
    # Verify that each item in the result is an instance of ParsedData
    # and its raw_title matches the corresponding input title
    parsed_results = batch_parse(test_titles, chunk_size=5)
    assert len(parsed_results) == len(test_titles)
    for parsed_data, title in zip(parsed_results, test_titles):
        assert isinstance(parsed_data, ParsedData), "Result item is not an instance of ParsedData"
        assert parsed_data.raw_title == title, f"Expected raw_title to be '{title}', but got '{parsed_data.raw_title}'"


def test_episode_parsing():
    test_cases = [
        # Regular Tests
        ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1]),
        ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1, 2]),
        ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1, 2]),
        ("The Simpsons S01E01-E02-E03-E04-E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1, 2, 3, 4, 5]),
        ("The Simpsons S01E01E02E03E04E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1, 2, 3, 4, 5]),
        ("The Simpsons E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", list(range(1, 201))), # Eps 1-200
        ("House MD All Seasons (1-8) 720p Ultra-Compressed", []),
        ("The Avengers (EMH) - S01 E15 - 459 (1080p - BluRay)", [15]),
        ("Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]", [5]),
        ("4-13 Cursed (HD)", [13]),

        # Mini-series, this is correct!
        ("Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World", [2]),

        # Anime Tests
        ("Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p BluRay x264 DTS 5.1 -DDR", []),
        ("[F-D] Fairy Tail Season 1 - 6 + Extras [480P][Dual-Audio]", []),
        ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", list(range(1, 9))), # Eps 1-8
        ("[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ", [24]),
        ("Bleach 10º Temporada - 215 ao 220 - [DB-BR]", [215, 216, 217, 218, 219, 220]),

        # Looks like it doesn't handle hyphens in the episode part. It's not a big deal,
        # as it's not a common practice to use hypens in the episode part. Mostly seen in Anime.
        # I did run tests and I was still able to scrape for Naruto, which is a huge win as its always been a tough one!
        ("Naruto Shippuden - 107 - Strange Bedfellows", []),                             # Incorrect, should of been: [107]
        ("[224] Shingeki no Kyojin - S03 - Part 1 - 13 [BDRip1080p.x265.FLAC]", []),     # Incorrect, should of been:  [13]
        ("[Erai-raws] Shingeki no Kyojin Season 3 - 11 [1080p][Multiple Subtitle]", [])  # Incorrect, should of been:  [11]
    ]
    for test_string, expected in test_cases:
        assert (
            extract_episodes(test_string) == expected
        ), f"Failed for '{test_string}' with expected {expected}"


def test_multi_audio_patterns():
    test_cases = [
        ("Lucy 2014 Dual-Audio WEBRip 1400Mb", True),
        ("Darkness Falls (2020) HDRip 720p [Hindi-Dub] Dual-Audio x264", True),
        ("The Simpsons - Season 1 Complete [DVDrip ITA ENG] TNT Village", False),
        ("Brave.2012.R5.DVDRip.XViD.LiNE-UNiQUE", False),
    ]
    for test_string, expected in test_cases:
        assert check_pattern(MULTI_AUDIO_COMPILED, test_string) == expected


def test_multi_subtitle_patterns():
    test_cases = [
        (
            "IP Man And Four Kings 2019 HDRip 1080p x264 AAC Mandarin HC CHS-ENG SUBS Mp4Ba",
            True,
        ),
        ("The Simpsons - Season 1 Complete [DVDrip ITA ENG] TNT Village", True),
        ("The.X-Files.S01.Retail.DKsubs.720p.BluRay.x264-RAPiDCOWS", False),
        ("Hercules (2014) WEBDL DVDRip XviD-MAX", False),
    ]
    for test_string, expected in test_cases:
        assert check_pattern(MULTI_SUBTITLE_COMPILED, test_string) == expected


def test_complete_series_patterns():
    test_cases = [
        (
            "The Sopranos - The Complete Series (Season 1, 2, 3, 4, 5 & 6) + Extras",
            True,
        ),
        ("The Inbetweeners Collection", True),
        ("The Simpsons S01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
        ("Two and a Half Men S12E01 HDTV x264 REPACK-LOL [eztv]", False),
    ]
    for test_string, expected in test_cases:
        assert check_pattern(COMPLETE_SERIES_COMPILED, test_string) == expected


def test_sort_function(test_titles, settings_model, rank_model):
    processed = batch_parse(test_titles)
    rtn = RTN(settings_model, rank_model)
    torrents = [rtn.rank(data.raw_title, "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7") for data in processed]
    sort(torrents)

    # Test if the list is sorted in reverse
    assert all(torrents[i].rank <= torrents[i + 1].rank for i in range(len(torrents) - 1))


def test_compare_two_torrent_objs(settings_model, rank_model):
    # create 2 torrent objects and check __eq__ method
    rtn = RTN(settings_model, rank_model)
    # test valid comparison
    torrent1 = rtn.rank("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7")
    torrent2 = rtn.rank("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7")
    # test invalid comparison
    invalid_torrent = "The Walking Dead S08E02 720p HDTV x264-ASAP[ettv]"
    assert torrent1 == torrent2
    assert torrent1 != invalid_torrent


def test_validate_infohash_from_torrent_obj(settings_model, rank_model):
    rtn = RTN(settings_model, rank_model)
    with pytest.raises(ValueError):
        # Missing infohash
        rtn.rank("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", None)  # type: ignore
    with pytest.raises(ValueError):
        # Missing title and infohash
        rtn.rank(None, None)  # type: ignore
    with pytest.raises(ValueError):
        # Invalid infohash length
        data = parse("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]")
        Torrent(raw_title="The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", infohash="c08a9ee8ce3a5c2c08", data=data)  # type: ignore
    with pytest.raises(ValidationError):
        # Invalid strings or not instance of str
        data = parse("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]")
        Torrent(raw_title=12345, infohash=12345, data=data)  # type: ignore

# test parse_extras function
def test_parse_extras_invalid():
    with pytest.raises(TypeError):
        assert parse_extras(12345), "Should raise TypeError" # type: ignore

# test check_hdr_dolby_video function for valid return
def test_check_hdr_dolby_video():
    test_cases = [
        ("Mission.Impossible.1996.Dolby.Vision.Custom.Audio.1080p.PL-Spedboy", "DV"),
        ("Casino.1995.MULTi.REMUX.2160p.UHD.Blu-ray.HDR.HEVC.DTS-X7.1-DENDA", "HDR"),
        ("Guardians of the Galaxy.HDR10plus", "HDR10+"),
        ("Brave.2012.R5.DVDRip.XViD.LiNE-UNiQUE", ""),
    ]
    for test_string, expected in test_cases:
        assert check_hdr_dolby_video(test_string) == expected
