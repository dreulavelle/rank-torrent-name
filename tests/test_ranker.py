# import pytest
# from PTN import (
#     BaseRankingModel,
#     DefaultRanking,
#     ParsedData,
#     SettingsModel,
#     Torrent,
#     get_rank,
#     parse,
# )


# @pytest.fixture
# def settings_model():
#     return SettingsModel()

# @pytest.fixture
# def custom_settings():
#     return SettingsModel(
#         profile="custom",
#         require=[],
#         exclude=[],
#         preferred=[r"\bS\d+"],
#         custom_ranks={
#             "uhd": {"enable": True, "fetch": True, "rank": -200},
#             "fhd": {"enable": True, "fetch": True, "rank": 90},
#             "hd": {"enable": True, "fetch": True, "rank": 60},
#             "sd": {"enable": True, "fetch": True, "rank": -120},
#             "dolby_video": {"enable": True, "fetch": True, "rank": -1000},
#             "hdr": {"enable": True, "fetch": True, "rank": -1000},
#             "hdr10": {"enable": True, "fetch": True, "rank": -1000},
#             "aac": {"enable": True, "fetch": True, "rank": 70},
#             "ac3": {"enable": True, "fetch": True, "rank": 50},
#             "remux": {"enable": False, "fetch": True, "rank": -75},
#             "webdl": {"enable": True, "fetch": True, "rank": 90},
#             "bluray": {"enable": True, "fetch": True, "rank": -90},
#         },
#     )


# test_data = [
#     (
#         "Jumanji (1995) RM4K (1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole",
#         {
#             "raw_title": "Jumanji (1995) RM4K (1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole",
#             "parsed_title": "Jumanji",
#             "fetch": True,
#             "year": [1995],
#             "resolution": ["1080p"],
#             "quality": ["Blu-ray"],
#             "codec": ["H.265"],
#             "audio": ["AAC 5.1"],
#             "bitDepth": [10],
#         },
#     ),
#     (
#         "The Simpsons - Complete Seasons S01 to S28 (1080p, 720p, DVDRip)",
#         {
#             "raw_title": "The Simpsons - Complete Seasons S01 to S28 (1080p, 720p, DVDRip)",
#             "parsed_title": "The Simpsons",
#             "fetch": True,
#             "is_complete": True,
#             "resolution": ["1080p"],
#             "quality": ["DVD-Rip"],
#             "season": list(range(1, 29)),
#         },
#     ),
# ]

# test_ids = ["FullQualityCheck", "SeasonRangeCheck"]

# def test_valid_torrent_from_item():
#     ranking_model = DefaultRanking()
#     torrent = Torrent(
#         ranking_model=ranking_model,
#         raw_title="The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]",
#         infohash="1234567890",
#     )

#     assert isinstance(torrent, Torrent)
#     assert isinstance(torrent.parsed_data, ParsedMediaItem)
#     assert torrent.raw_title == "The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]"
#     assert torrent.infohash == "1234567890"
#     assert torrent.parsed_data.parsed_title == "The Walking Dead"
#     assert torrent.parsed_data.fetch is True
#     assert torrent.rank == 163, f"Rank was {torrent.rank} instead of 163"

# @pytest.mark.parametrize("raw_title, expected", test_data, ids=test_ids)
# def test_parsed_media_item_properties(raw_title: str, expected: dict):
#     item = ParsedMediaItem(raw_title=raw_title)
#     for key, value in expected.items():
#         assert (
#             getattr(item, key) == value
#         ), f"Attribute {key} failed for raw_title: {raw_title}"