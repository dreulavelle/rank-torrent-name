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


@pytest.fixture
def ranking_model():
    return DefaultRanking()

@pytest.fixture
def custom_ranking_model():
    return BaseRankingModel(
        uhd=140,
        fhd=100,
        hd=50,
        sd=-100,
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
    assert isinstance(torrent.parsed_data, ParsedData)
    assert torrent.raw_title == "The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]"
    assert torrent.infohash == "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7"
    assert torrent.parsed_data.parsed_title == "The Walking Dead"
    assert torrent.parsed_data.fetch is False
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