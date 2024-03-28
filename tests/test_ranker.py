import pytest

from RTN import RTN
from RTN.models import (
    BaseRankingModel,
    CustomRank,
    DefaultRanking,
    ParsedData,
    SettingsModel,
)
from RTN.parser import Torrent
from RTN.ranker import get_rank


@pytest.fixture
def ranking_model():
    return DefaultRanking()

@pytest.fixture
def custom_ranking_model():
    return BaseRankingModel(
        uhd=140,
        fhd=100,
        hd=50,
        sd=-10,
        dolby_video=-1000,
        hdr=-1000,
        hdr10=-1000,
        aac=70,
        ac3=50,
        remux=-75,
        webdl=90,
        bluray=-90,
    )

@pytest.fixture
def settings_model():
    return SettingsModel()

@pytest.fixture
def custom_settings_model():
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


def test_valid_torrent_from_title(settings_model, ranking_model):
    rtn = RTN(settings_model, ranking_model)

    torrent = rtn.rank("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]",
                       "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7")

    assert isinstance(torrent, Torrent)
    assert isinstance(torrent.data, ParsedData)
    assert torrent.raw_title == "The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]"
    assert torrent.infohash == "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7"
    assert torrent.data.parsed_title == "The Walking Dead"
    assert torrent.data.fetch is False
    assert torrent.rank > 0, f"Rank was {torrent.rank} instead of 163"
    assert torrent.lev_ratio > 0.0, f"Levenshtein ratio was {torrent.lev_ratio} instead of > 0.0"

def test_invalid_torrent_from_title(settings_model, ranking_model):
    rtn = RTN(settings_model, ranking_model)

    with pytest.raises(TypeError):
        # Missing 2 string arguments
        rtn.rank("c08a9ee8ce3a5c2c08865e2b05406273cabc97e7") # type: ignore
    with pytest.raises(ValueError):
        # Missing title
        rtn.rank(None, "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7") # type: ignore
    with pytest.raises(ValueError):
        # Missing infohash
        rtn.rank("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", None) # type: ignore
    with pytest.raises(ValueError):
        # Missing title and infohash
        rtn.rank(None, None) # type: ignore
    with pytest.raises(TypeError):
        # Invalid title type
        rtn.rank(123, "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7") # type: ignore
    with pytest.raises(TypeError):
        # Invalid infohash type
        rtn.rank("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", 123) # type: ignore
    with pytest.raises(ValueError):
        # Invalid infohash length
        rtn.rank("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", "c08a9ee8ce3a5c2c0886")
    with pytest.raises(ValueError):
        # test if not parsed_data
        rtn.rank("", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7") # type: ignore

def test_valid_rtn_object(settings_model, ranking_model):
    rtn = RTN(settings_model, ranking_model)
    assert isinstance(rtn, RTN)
    assert isinstance(rtn.settings, SettingsModel)
    assert isinstance(rtn.ranking_model, BaseRankingModel)

def test_invalid_rtn_object(settings_model, ranking_model):
    with pytest.raises(ValueError):
        # Missing settings
        RTN(None, ranking_model) # type: ignore
    with pytest.raises(ValueError):
        # Missing ranking_model
        RTN(settings_model, None) # type: ignore
    with pytest.raises(TypeError):
        # Invalid settings type
        RTN(123, ranking_model) # type: ignore
    with pytest.raises(TypeError):
        # Invalid ranking_model type
        RTN(settings_model, 123) # type: ignore

def test_rank_calculation_accuracy(settings_model, ranking_model):
    parsed_data = ParsedData(
        parsed_title="Example Movie",
        raw_title="Example.Movie.2020.1080p.BluRay.x264-Example",
        resolution=["1080p"],
        quality=["Blu-ray"],
        codec=["H.264"],
        audio=["Dolby Digital"],
        hdr="HDR10",
        is_complete=True,
        season=[1],
        episode=[1],
    )

    rank = get_rank(parsed_data, settings_model, ranking_model)
    assert rank == 273, f"Expected rank did not match, got {rank}"

def test_batch_ranking(settings_model, ranking_model):
    rtn = RTN(settings_model, ranking_model)
    torrents = [
        ("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7"),
        ("Example.Movie.2020.1080p.BluRay.x264-Example", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e8"),
        ("Example.Series.S2.2020", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e9"),
    ]

    ranked_torrents = rtn.batch_rank(torrents)
    assert len(ranked_torrents) == 3
    for torrent in ranked_torrents:
        assert isinstance(torrent, Torrent)
        assert isinstance(torrent.data, ParsedData)
        assert torrent.fetch is True
        assert torrent.rank > 0, f"Rank was {torrent.rank} instead of > 0"
        assert torrent.lev_ratio > 0.0, f"Levenshtein ratio was {torrent.lev_ratio} instead of > 0.0"

def test_preference_handling(custom_settings_model, ranking_model):
    # Test with preferred title with a preference for Season number in title
    # to make sure we can check before-after case. User should be able to set
    # their own preferred patterns dynamically.
    parsed_data = ParsedData(raw_title="Example.Series.S2.2020", parsed_title="Example Series")
    rank_with_preference = get_rank(parsed_data, custom_settings_model, ranking_model)
    assert rank_with_preference == 5000, "Preferred title should have rank 5000"
    custom_settings_model.preferred = []
    rank_without_preference = get_rank(parsed_data, custom_settings_model, ranking_model)
    assert rank_with_preference > rank_without_preference, "Preferred title should have higher rank"


def test_resolution_ranking(settings_model, ranking_model):
    # Test Valid Resolutions
    parsed_data_4k = ParsedData(raw_title="4K", parsed_title="4K", resolution=["4K"])
    parsed_data_2160p = ParsedData(raw_title="2160p", parsed_title="2160p", resolution=["2160p"])
    parsed_data_1440p = ParsedData(raw_title="1440p", parsed_title="1440p", resolution=["1440p"])
    parsed_data_1080p = ParsedData(raw_title="1080p", parsed_title="1080p", resolution=["1080p"])
    parsed_data_720p = ParsedData(raw_title="720p", parsed_title="720p", resolution=["720p"])
    parsed_data_480p = ParsedData(raw_title="480p", parsed_title="480p", resolution=["480p"])
    # Test Invalid Resolution
    parsed_data_none = ParsedData(raw_title="None", parsed_title="None", resolution=[])

    rank_4k = get_rank(parsed_data_4k, settings_model, ranking_model)
    rank_2160p = get_rank(parsed_data_2160p, settings_model, ranking_model)
    rank_1440p = get_rank(parsed_data_1440p, settings_model, ranking_model)
    rank_1080p = get_rank(parsed_data_1080p, settings_model, ranking_model)
    rank_720p = get_rank(parsed_data_720p, settings_model, ranking_model)
    rank_480p = get_rank(parsed_data_480p, settings_model, ranking_model)
    rank_none = get_rank(parsed_data_none, settings_model, ranking_model)

    assert rank_4k > rank_1080p, "4K resolution should have higher rank than 1080p"
    assert rank_2160p > rank_1080p, "2160p resolution should have higher rank than 1080p"
    assert rank_1440p > rank_1080p, "1440p resolution should have higher rank than 1080p"
    assert rank_1080p > rank_720p, "1080p resolution should have higher rank than 720p"
    assert rank_720p > rank_480p, "720p resolution should have higher rank than 480p"
    assert rank_480p < 0, "480p resolution should have negative rank"
    assert rank_none == 0, "No resolution should have rank 0"