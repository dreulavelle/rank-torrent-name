import pytest

from RTN import parse
from RTN.extras import episodes_from_season, extract_episodes, title_match
from RTN.models import ParsedData


@pytest.mark.parametrize("test_string, expected_data", [
    (
        "The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole",
        {
            "raw_title": "The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole",
            "parsed_title": "The Simpsons",
            "year": None,
            "resolution": "1080p",
            "quality": "BluRay",
            "seasons": [1],
            "episodes": [1, 2],
            "codec": "hevc",
            "audio": ["AAC"],
            "languages": [],
            "bit_depth": "10bit"
        }
    ),
])
def test_parsed_data_model(test_string, expected_data):
    data = parse(test_string)
    assert isinstance(data, ParsedData)
    assert data.raw_title == expected_data["raw_title"]
    assert data.parsed_title == expected_data["parsed_title"]
    assert data.year == expected_data["year"]
    assert data.resolution == expected_data["resolution"]
    assert data.quality == expected_data["quality"]
    assert data.seasons == expected_data["seasons"]
    assert data.episodes == expected_data["episodes"]
    assert data.codec == expected_data["codec"]
    assert data.audio == expected_data["audio"]
    assert data.languages == expected_data["languages"]
    assert data.bit_depth == expected_data["bit_depth"]


@pytest.mark.parametrize("title, query, expected", [
    ("Damsel", "Damsel (2024)", False),
    ("The Simpsons", "The Simpsons", True),
    ("The Simpsons", "The Simpsons Movie", False),
    ("The Simpsons", "The Simpsons S01E01", False),
    ("The Simpsons S01E01", "The Simpsons S01E01", True),
    ("The Simpsons Movie", "The Simpsons Movie", True),
    ("American Horror Story", "American Story Horror", False),
])
def test_default_title_matching(title, query, expected):
    """Test the title_match function"""
    assert title_match(title, query) == expected, f"Failed for {title} and {query}"


@pytest.mark.parametrize("release_name, expected", [
    ("www.5MovieRulz.show - Khel Khel Mein (2024) 1080p Hindi DVDScr - x264 - AAC - 2.3GB.mkv", {
        "raw_title": "www.5MovieRulz.show - Khel Khel Mein (2024) 1080p Hindi DVDScr - x264 - AAC - 2.3GB.mkv",
        "parsed_title": "Khel Khel Mein",
        "year": 2024,
        "languages": ["hi"],
        "seasons": [],
        "episodes": [],
        "quality": "SCR",
        "codec": "avc",
        "audio": ["AAC"],
        "resolution": "1080p",
        "container": "mkv",
        "extension": "mkv",
        "size": "2.3GB",
        "site": "www.5MovieRulz.show",
        "trash": True
    })
])
def test_random_releases_parse(release_name, expected):
    assert parse(release_name, json=True) == expected, f"Failed with {expected}"


@pytest.mark.parametrize("release_name, expected", [
    ("www.5MovieRulz.show - Khel Khel Mein (2024) 1080p Hindi DVDScr - x264 - AAC - 2.3GB.mkv", ParsedData(
        raw_title="www.5MovieRulz.show - Khel Khel Mein (2024) 1080p Hindi DVDScr - x264 - AAC - 2.3GB.mkv",
        parsed_title="Khel Khel Mein",
        normalized_title="khel khel mein",
        trash=True,
        year=2024,
        resolution="1080p",
        seasons=[],
        episodes=[],
        languages=["hi"],
        quality="SCR",
        codec="avc",
        audio=["AAC"],
        container="mkv",
        extension="mkv",
        site="www.5MovieRulz.show",
        size="2.3GB"
    ))
])
def test_random_releases_parse(release_name, expected):
    assert parse(release_name) == expected


@pytest.mark.parametrize("title, query, threshold, expected_exception", [
    ("The Simpsons", 12345, None, TypeError),  # test not correct_title or not raw_title
    ("The Simpsons", "The Simpsons", 0.9, None),  # test valid threshold
    ("The Simpsons", "The Simpsons", 1.1, ValueError),  # test invalid threshold
    (None, None, None, ValueError),  # test not correct_title or not raw_title
])
def test_title_matching_exceptions(title, query, threshold, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            assert title_match(title, query, threshold)  # type: ignore
    else:
        assert title_match(title, query, threshold)


@pytest.mark.parametrize("test_string, expected", [
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

    # Mini-series (this is correct)
    ("Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World", [2]),

    # Anime Tests
    ("Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p BluRay x264 DTS 5.1 -DDR", []),
    ("[F-D] Fairy Tail Season 1 - 6 + Extras [480P][Dual-Audio]", []),
    ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", list(range(1, 9))), # Eps 1-8
    ("[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ", [24]),
    ("Bleach 10º Temporada - 215 ao 220 - [DB-BR]", [215, 216, 217, 218, 219, 220]),
    ("Naruto Shippuden - 107 - Strange Bedfellows", [107]),
    ("[224] Shingeki no Kyojin - S03 - Part 1 - 13 [BDRip1080p.x265.FLAC]", [13]),

    # User submitted edge cases
    ("Joker.2019.PROPER.mHD.10Bits.1080p.BluRay.DD5.1.x265-TMd.mkv", []),

    # Incorrect, should of been: [11]
    ("[Erai-raws] Shingeki no Kyojin Season 3 - 11 [1080p][Multiple Subtitle]", []),
])
def test_episode_parsing(test_string, expected):
    assert extract_episodes(test_string) == expected, f"Failed for '{test_string}' with expected {expected}"


@pytest.mark.parametrize("test_string, expected", [
    # Shows
    ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "show"),
    ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "show"),
    ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "show"),
    ("The Simpsons S01E01-E02-E03-E04-E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "show"),
    ("The Simpsons S01E01E02E03E04E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "show"),
    ("The Simpsons E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "show"),
    ("House MD All Seasons (1-8) 720p Ultra-Compressed", "show"),
    ("Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World", "show"),
    ("Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]", "show"),
    ("[F-D] Fairy Tail Season 1 - 6 + Extras [480P][Dual-Audio]", "show"),
    ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", "show"),
    ("[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ", "show"),

    # Movies
    ("The Avengers (EMH) - (1080p - BluRay)", "movie"),
    ("Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p BluRay x264 DTS 5.1 -DDR", "movie"),
    ("Joker.2019.PROPER.mHD.10Bits.1080p.BluRay.DD5.1.x265-TMd.mkv", "movie"),
    ("Hercules.2014.EXTENDED.1080p.WEB-DL.DD5.1.H264-RARBG", "movie"),
    ("Brave.2012.R5.DVDRip.XViD.LiNE-UNiQUE", "movie"),
    ("Dawn.Of.The.Planet.of.The.Apes.2014.1080p.WEB-DL.DD51.H264-RARBG", "movie"),
    ("One Shot [2014] DVDRip XViD-ViCKY", "movie"),
    ("Impractical.Jokers.The.Movie.2020.1080p.WEBRip.x264.AAC5.1", "movie"),
    ("The.Meg.2018.1080p.HDRip.x264.[ExYu-Subs]", "movie"),
    ("Guardians of the Galaxy (2014) Dual Audio DVDRip AVI", "movie"),
    ("UFC.179.PPV.HDTV.x264-Ebi[rartv]", "movie"),
    ("Hercules", "movie")
])
def test_get_media_type(test_string, expected):
    data = parse(test_string)
    assert data.type == expected, f"Failed for '{test_string}' with expected `{expected}`"


@pytest.mark.parametrize("raw_title, season_num, expected", [
    ("", 1, pytest.raises(ValueError)), # no title should raise exception
    ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", 1, [1, 2]),
    ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", 2, []),
    ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "rice", pytest.raises(TypeError)),
    ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", None, pytest.raises(ValueError)),
    ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", 1, [1]),
    ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", 1, [1, 2]),
    ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", 1, [1, 2]),
    ("The Simpsons S1 E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", 1, list(range(1, 201))),
    ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", 6, list(range(1, 9))), # Eps 1-8
    ("Game.of.Thrones.S08E01.1080p.WEB-DL.DDP5.1.H.264-GoT", 8, [1]),
])
def test_extract_episode_from_season(raw_title, season_num, expected):
    if isinstance(expected, list):
        episodes = episodes_from_season(raw_title, season_num)
        assert episodes == expected, f"Failed for '{raw_title}' with expected {expected}"
    else:
        with expected:
            episodes = episodes_from_season(raw_title, season_num)


@pytest.mark.parametrize("test_string, expected", [
    ("Yu-Gi-Oh! Zexal - 087 - Dual Duel, Part 1.mkv", [87]),
    ("Yu-Gi-Oh! Zexal - 089 - Darkness Dawns.mkv", [89]),
    ("Yu-Gi-Oh! Zexal - 090 - You Give Love a Bot Name.mkv", [90]),
    ("Yu-Gi-Oh! Zexal - 091 - Take a Chance.mkv", [91]),
    ("Yu-Gi-Oh! Zexal - 093 - An Imperfect Couple, Part 2.mkv", [93]),
    ("Yu-Gi-Oh! Zexal - 094 - Enter Vector.mkv", [94]),
])
def test_get_correct_episodes(test_string, expected):
    data = extract_episodes(test_string)
    assert data == expected, f"Failed for '{test_string}' with expected {expected}"


@pytest.mark.parametrize("test_string, expected", [
    # True
    ("Guardians of the Galaxy (CamRip / 2014)", True),  # CamRip
    ("Brave.2012.R5.DVDRip.XViD.LiNE-UNiQUE", True),    # R5, LiNE
    ("Avengers Infinity War 2018 NEW PROPER 720p HD-CAM X264 HQ-CPG", True),
    ("Venom: Let There Be Carnage (2021) English 720p CAMRip [NO LOGO]", True),
    ("Oppenheimer (2023) NEW ENG 1080p HQ-CAM x264 AAC - HushRips", True),
    ("Hatyapuri 2022 1080p CAMRp Bengali AAC H264 [2GB] - HDWebMovies", True),
    ("Avengers: Infinity War (2018) 720p HQ New CAMRip Line Audios [Tamil + Telugu + Hindi + Eng] x264 1.2GB [Team TR]", True),
    # False
    ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
    ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
    ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
    ("The Simpsons S01E01-E02-E03-E04-E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
    ("The Simpsons S01E01E02E03E04E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
    ("The Simpsons E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
    ("House MD All Seasons (1-8) 720p Ultra-Compressed", False),
    ("The Avengers (EMH) - S01 E15 - 459 (1080p - BluRay)", False),
    ("Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World", False),
    ("Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]", False),
    ("Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p BluRay x264 DTS 5.1 -DDR", False),
    ("[F-D] Fairy Tail Season 1 - 6 + Extras [480P][Dual-Audio]", False),
    ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", False),
    ("[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ", False),
    ("Bleach 10º Temporada - 215 ao 220 - [DB-BR]", False),
    ("Naruto Shippuden - 107 - Strange Bedfellows", False),
    ("[224] Shingeki no Kyogin - S03 - Part 1 - 13 [BDRip.1080p.x265.FLAC]", False),
    ("[Erai-raws] Shingeki no Kyogin Season 3 - 11 [1080p][Multiple Subtitle]", False),
])
def test_trash_coverage(test_string, expected):
    data = parse(test_string)
    assert data.trash == expected, f"Failed for '{test_string}' with expected {expected}"


@pytest.mark.parametrize("test_string, expected_season, expected_episode", [
    ("3.10.to.Yuma.2007.1080p.BluRay.x264.DTS-SWTYBLZ.mkv", [], []),
    ("30.Minutes.or.Less.2011.1080p.BluRay.X264-SECTOR7.mkv", [], []),
    ("Alien.Covenant.2017.1080p.BluRay.x264-SPARKS[EtHD].mkv", [], []),
    ("Alien.1979.REMASTERED.THEATRICAL.1080p.BluRay.x264.DTS-SWTYBLZ.mkv", [], []),
    ("The Steve Harvey Show - S02E07 - When the Funk Hits the Rib Tips.mkv", [2], [7]),
    ("Fantastic.Beasts.The.Crimes.Of.Grindelwald.2018.4K.HDR.2160p.BDRip Ita Eng x265-NAHOM.mkv", [], []),
    ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1], [1]),
    ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1], [1, 2]),
    ("House MD All Seasons (1-8) 720p Ultra-Compressed", [1, 2, 3, 4, 5, 6, 7, 8], []),
    ("The Avengers (EMH) - S01 E15 - 459 (1080p - BluRay)", [1], [15]),
    ("Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World", [], [2]),
    ("Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]", [6], [5]),
    ("The Joker (2019) 1080p WEB-DL x264 - YIFY", [], []),
])
def test_season_episode_extraction(test_string, expected_season, expected_episode):
    item = parse(test_string)
    assert isinstance(item, ParsedData), f"Failed for '{test_string}', expected ParsedData object"
    assert item.seasons == expected_season, f"Failed for '{test_string}' with expected {expected_season}"
    assert item.episodes == expected_episode, f"Failed for '{test_string}' with expected {expected_episode}"
