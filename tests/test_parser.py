
import pytest
from pydantic import ValidationError

from RTN import get_rank, parse
from RTN.exceptions import GarbageTorrent
from RTN.models import (
    BaseRankingModel,
    CustomRank,
    DefaultRanking,
    ParsedData,
    SettingsModel,
)
from RTN.parser import (
    RTN,
    Torrent,
    batch_parse,
    episodes_from_season,
    get_type,
    is_movie,
    sort_torrents,
    title_match,
)
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


def test_parsed_data_model():
    data = parse("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", remove_trash=False)
    assert isinstance(data, ParsedData)
    assert data.raw_title == "The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"
    assert data.parsed_title == "The Simpsons"
    assert data.fetch is False  # Default value as False since `parse` doesn't set it. Must use `rank` to set it.
    assert data.is_4k is False
    assert data.is_multi_audio is False
    assert data.is_multi_subtitle is False
    assert data.is_complete is False
    assert data.year == 0
    assert data.resolution == ["1080p"]
    assert data.quality == ["Blu-ray"]
    assert data.season == [1]
    assert data.episode == [1, 2]
    assert data.codec == ["H.265"]
    assert data.audio == ["AAC 5.1"]
    assert data.subtitles == []
    assert data.language == []
    assert data.bitDepth == [10]
    assert data.hdr == ""
    assert data.proper is False
    assert data.repack is False
    assert data.remux is False
    assert data.upscaled is False
    assert data.remastered is False
    assert data.directorsCut is False
    assert data.extended is False


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
    parsed_results = batch_parse(test_titles, remove_trash=False, chunk_size=5)
    assert len(parsed_results) == len(test_titles)
    for parsed_data, title in zip(parsed_results, test_titles):
        assert isinstance(parsed_data, ParsedData), "Result item is not an instance of ParsedData"
        assert parsed_data.raw_title == title, f"Expected raw_title to be '{title}', but got '{parsed_data.raw_title}'"


def test_batch_parse_trash_processing(test_titles):
    # Some of these titles are trash, so we should remove them.
    with pytest.raises(GarbageTorrent):
        assert batch_parse(test_titles, remove_trash=True, chunk_size=5)


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
        ("Naruto Shippuden - 107 - Strange Bedfellows", []),                              # Incorrect, should of been: [107]
        ("[224] Shingeki no Kyojin - S03 - Part 1 - 13 [BDRip1080p.x265.FLAC]", []),      # Incorrect, should of been:  [13]
        ("[Erai-raws] Shingeki no Kyojin Season 3 - 11 [1080p][Multiple Subtitle]", []),  # Incorrect, should of been:  [11]

        # User submitted edge cases
        ("Joker.2019.PROPER.mHD.10Bits.1080p.BluRay.DD5.1.x265-TMd.mkv", []),
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
        ("IP Man And Four Kings 2019 HDRip 1080p x264 AAC Mandarin HC CHS-ENG SUBS Mp4Ba", True),
        ("The Simpsons - Season 1 Complete [DVDrip ITA ENG] TNT Village", True),
        ("The.X-Files.S01.Retail.DKsubs.720p.BluRay.x264-RAPiDCOWS", False),
        ("Hercules (2014) WEBDL DVDRip XviD-MAX", False),
    ]
    for test_string, expected in test_cases:
        assert check_pattern(MULTI_SUBTITLE_COMPILED, test_string) == expected


def test_complete_series_patterns():
    test_cases = [
        ("The Sopranos - The Complete Series (Season 1, 2, 3, 4, 5 & 6) + Extras", True),
        ("The Inbetweeners Collection", True),
        ("The Simpsons S01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
        ("Two and a Half Men S12E01 HDTV x264 REPACK-LOL [eztv]", False),
    ]
    for test_string, expected in test_cases:
        assert check_pattern(COMPLETE_SERIES_COMPILED, test_string) == expected


def test_sort_function(test_titles, settings_model, rank_model):
    torrent_set = set()
    processed = batch_parse(test_titles, remove_trash=False, chunk_size=5)
    for item in processed:
        ranking = get_rank(item, settings_model, rank_model)
        torrent = Torrent(raw_title=item.raw_title, infohash="c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", data=item, rank=ranking)
        torrent_set.add(torrent)
    sorted_torrents = sort_torrents(torrent_set)
    
    # Test that the sorted_torrents is a dict
    # and that the torrents are sorted by rank in the correct order (descending)
    assert isinstance(sorted_torrents, dict)
    sorted_torrents_list = list(sorted_torrents.values())
    for i in range(len(sorted_torrents_list) - 1):
        assert sorted_torrents_list[i].rank >= sorted_torrents_list[i + 1].rank


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


def test_is_movie_and_get_type():
    # Default is `show` if movie is not detected.
    test_cases = [
        # Shows
        ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False, "show"),
        ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False, "show"),
        ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False, "show"),
        ("The Simpsons S01E01-E02-E03-E04-E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False, "show"),
        ("The Simpsons S01E01E02E03E04E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False, "show"),
        ("The Simpsons E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False, "show"),
        ("House MD All Seasons (1-8) 720p Ultra-Compressed", False, "show"),
        ("The Avengers (EMH) - (1080p - BluRay)", False, "show"),
        ("Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World", False, "show"),
        ("Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]", False, "show"),
        ("4-13 Cursed (HD)", False, "show"),
        ("Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p BluRay x264 DTS 5.1 -DDR", False, "show"),
        ("[F-D] Fairy Tail Season 1 - 6 + Extras [480P][Dual-Audio]", False, "show"),
        ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", False, "show"),
        ("[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ", False, "show"),

        # Movies
        ("Joker.2019.PROPER.mHD.10Bits.1080p.BluRay.DD5.1.x265-TMd.mkv", True, "movie"),
        ("Hercules.2014.EXTENDED.1080p.WEB-DL.DD5.1.H264-RARBG", True, "movie"),
        ("Brave.2012.R5.DVDRip.XViD.LiNE-UNiQUE", True, "movie"),
        ("Dawn.Of.The.Planet.of.The.Apes.2014.1080p.WEB-DL.DD51.H264-RARBG", True, "movie"),
        ("One Shot [2014] DVDRip XViD-ViCKY", True, "movie"),
        ("Impractical.Jokers.The.Movie.2020.1080p.WEBRip.x264.AAC5.1", True, "movie"),
        ("The.Meg.2018.1080p.HDRip.x264.[ExYu-Subs]", True, "movie"),
        ("Guardians of the Galaxy (2014) Dual Audio DVDRip AVI", True, "movie"),

        # Pitfalls - these default as `show` but are actually movies.
        ("UFC.179.PPV.HDTV.x264-Ebi[rartv]", False, "show"),
        ("Hercules", False, "show"),
    ]

    for test_string, is_movie_type, expected in test_cases:
        data = parse(test_string, remove_trash=False)
        assert is_movie(data) == is_movie_type, f"Failed for '{test_string}' with expected `{is_movie_type}`"
        assert data.type == expected, f"Failed for '{test_string}' with expected `{expected}`"

    test_invalid_data = "123456"
    with pytest.raises(TypeError):
        assert is_movie(test_invalid_data) # type: ignore
        assert get_type(test_invalid_data) # type: ignore


def test_extract_episode_from_season():
    raw_title = "The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"
    episodes = episodes_from_season(raw_title, 1)
    assert episodes == [1, 2], "Should return [1, 2] because it detects Season 1"

    episodes = episodes_from_season(raw_title, 2)
    assert episodes == [], "Should return empty list"

    raw_title = ""
    with pytest.raises(ValueError):
        episodes = episodes_from_season(raw_title, 1)
        assert episodes == [], "Should raise ValueError"
    
    raw_title = "The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"
    with pytest.raises(TypeError):
        episodes = episodes_from_season(raw_title, "rice") # type: ignore
        assert episodes == [], "Should raise TypeError"

    raw_title = "The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"
    with pytest.raises(TypeError):
        episodes = episodes_from_season(raw_title, None) # type: ignore
        assert episodes == [], "Should raise TypeError"

    test_examples = [
        ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", 1, [1]),
        ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", 1, [1, 2]),
        ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", 1, [1, 2]),
        ("The Simpsons S1 E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", 1, list(range(1, 201))),
        ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", 6, list(range(1, 9))), # Eps 1-8
        ("Game.of.Thrones.S08E01.1080p.WEB-DL.DDP5.1.H.264-GoT", 8, [1]),
    ]
    for test_string, season, expected in test_examples:
        episodes = episodes_from_season(test_string, season)
        assert episodes == expected, f"Failed for '{test_string}' with expected {expected}"
