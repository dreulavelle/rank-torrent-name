import pytest

from RTN import RTN
from RTN.exceptions import GarbageTorrent
from RTN.models import (
    BaseRankingModel,
    CustomRank,
    DefaultRanking,
    ParsedData,
    SettingsModel,
)
from RTN.parser import Torrent
from RTN.ranker import calculate_preferred, get_rank


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
        avc=0,
        hevc=0,
        av1=0,
        h264=0,
        h265=0,
    )

@pytest.fixture
def enabled_ranking_model():
    return BaseRankingModel(
        uhd=4,
        fhd=3,
        hd=2,
        sd=-1,
        bluray=1,
        hdr=1,
        hdr10=1,
        dolby_video=1,
        dts_x=1,
        dts_hd=1,
        dts_hd_ma=1,
        atmos=1,
        truehd=1,
        ddplus=1,
        ac3=1,
        remux=1,
        webdl=1,
        repack=1,
        proper=1,
        dubbed=1,
        subbed=1,
        av1=1,
        brrip=1,
        h264=1,
        h265=1,
        bdrip=1,
        dvdrip=1,
        avc=1,
        hevc=1,
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
            "dvdrip": CustomRank(enable=True, fetch=True, rank=-90),
            "avc": CustomRank(enable=True, fetch=True, rank=-90),
            "hevc": CustomRank(enable=True, fetch=True, rank=-90),
            "av1": CustomRank(enable=True, fetch=True, rank=-90),
            "h264": CustomRank(enable=True, fetch=True, rank=-90),
            "h265": CustomRank(enable=True, fetch=True, rank=-90),
            "brrip": CustomRank(enable=True, fetch=True, rank=-90),
            "bdrip": CustomRank(enable=True, fetch=True, rank=-90),
        },
    )

@pytest.fixture
def enabled_settings_model():
    return SettingsModel(
        profile="default",
        require=[],
        exclude=[],
        preferred=[],
        custom_ranks={
            "uhd": CustomRank(enable=True, fetch=True, rank=4),
            "fhd": CustomRank(enable=True, fetch=True, rank=3),
            "hd": CustomRank(enable=True, fetch=True, rank=2),
            "sd": CustomRank(enable=True, fetch=True, rank=-1),
            "bluray": CustomRank(enable=True, fetch=True, rank=1),
            "hdr": CustomRank(enable=True, fetch=True, rank=1),
            "hdr10": CustomRank(enable=True, fetch=True, rank=1),
            "dolby_video": CustomRank(enable=True, fetch=True, rank=1),
            "dts_x": CustomRank(enable=True, fetch=True, rank=1),
            "dts_hd": CustomRank(enable=True, fetch=True, rank=1),
            "dts_hd_ma": CustomRank(enable=True, fetch=True, rank=1),
            "atmos": CustomRank(enable=True, fetch=True, rank=1),
            "truehd": CustomRank(enable=True, fetch=True, rank=1),
            "ddplus": CustomRank(enable=True, fetch=True, rank=1),
            "aac": CustomRank(enable=True, fetch=True, rank=1),
            "ac3": CustomRank(enable=True, fetch=True, rank=1),
            "remux": CustomRank(enable=True, fetch=True, rank=1),
            "webdl": CustomRank(enable=True, fetch=True, rank=1),
            "repack": CustomRank(enable=True, fetch=True, rank=1),
            "proper": CustomRank(enable=True, fetch=True, rank=1),
            "dubbed": CustomRank(enable=True, fetch=True, rank=1),
            "subbed": CustomRank(enable=True, fetch=True, rank=1),
            "av1": CustomRank(enable=True, fetch=True, rank=1),
        },
    )


def test_valid_torrent_from_title(settings_model, ranking_model):
    rtn = RTN(settings_model, ranking_model)

    torrent: Torrent = rtn.rank("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]",
                       "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", 
                       correct_title="The Walking Dead",
                       remove_trash=True
    )

    assert isinstance(torrent, Torrent)
    assert isinstance(torrent.data, ParsedData)
    assert torrent.raw_title == "The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]"
    assert torrent.infohash == "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7"
    assert torrent.data.parsed_title == "The Walking Dead"
    assert torrent.data.fetch is True, f"Fetch was {torrent.data.fetch} instead of True"
    assert torrent.fetch is True, f"Fetch was {torrent.fetch} instead of True"
    assert torrent.rank == 60, f"Rank was {torrent.rank} instead of 60"
    assert torrent.lev_ratio > 0.0, f"Levenshtein ratio was {torrent.lev_ratio} instead of > 0.0"


def test_invalid_torrent_from_title(settings_model, ranking_model):
    rtn = RTN(settings_model, ranking_model)

    with pytest.raises(GarbageTorrent):
        assert rtn.rank("The Walking Dead S05E03 CAM 720p HDTV x264-ASAP[ettv]",
                        "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", 
                        correct_title="The Walking Dead",
                        remove_trash=True
        )

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
    with pytest.raises(GarbageTorrent):
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
    )

    rank = get_rank(parsed_data, settings_model, ranking_model)
    assert rank == 60, f"Expected rank did not match, got {rank}"


def test_get_rank_validity(settings_model, ranking_model):
    parsed_data = ParsedData(
        raw_title="Example.Movie.2020.1080p.BluRay.x264-Example",
        parsed_title="Example Movie",
        resolution=["1080p"],
        quality=["Blu-ray"],
        codec=["H.264"],
        audio=["Dolby Digital"],
        hdr="HDR10",
        complete=True,
        repack=True,
        proper=True,
        seasons=[1],
        episodes=[1],
    )

    rank = get_rank(parsed_data, settings_model, ranking_model)
    assert isinstance(rank, int)
    assert rank < 0

    # test invalid get_rank with missing parsed_data
    parsed_data = ParsedData(
        raw_title="",
        parsed_title="Example Movie",
    )
    with pytest.raises(ValueError):
        get_rank(parsed_data, settings_model, ranking_model)

    # test invalid get_rank instance of ParsedData
    with pytest.raises(TypeError):
        get_rank(None, settings_model, ranking_model) # type: ignore


def test_valid_preferred_calculation(custom_settings_model):
    # use calculate_preferred function
    parsed_data = ParsedData(
        raw_title="Example.Series.S2.2020.Bluray",
        parsed_title="Example Series",
    )
    # test if preferred is not empty
    rank = calculate_preferred(parsed_data, custom_settings_model)
    assert rank == 5000, f"Expected rank did not match, got {rank}"

    parsed_data = ParsedData(
        raw_title="Example.Movie.2020.1080p-Example",
        parsed_title="Example Movie",
    )
    # test if preferred is empty
    rank = calculate_preferred(parsed_data, custom_settings_model)
    assert rank == 0, f"Expected rank did not match, got {rank}"


def test_batch_ranking_with_correct_title(settings_model, custom_ranking_model):
    rtn = RTN(settings_model, custom_ranking_model)
    torrents = [
        ("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7"),
        ("The Walking Dead.S2E18.1080p.BluRay.x264-Example", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e8"),
        ("The Walking Dead.S2.2020.1080p", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e9"),
    ]

    ranked_torrents = rtn.batch_rank(torrents, correct_title="The Walking Dead")
    assert len(ranked_torrents) == 3
    for torrent in ranked_torrents:
        assert isinstance(torrent, Torrent)
        assert isinstance(torrent.data, ParsedData)
        assert torrent.fetch is True
        assert torrent.rank > 0, f"Rank was {torrent.rank} instead of > 0"
        assert torrent.lev_ratio > 0.0, f"Levenshtein ratio was {torrent.lev_ratio} instead of > 0.0"


def test_batch_ranking_without_correct_title(settings_model, custom_ranking_model):
    rtn = RTN(settings_model, custom_ranking_model)
    torrents = [
        ("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7"),
        ("Example.Movie.2020.1080p.BluRay.x264-Example", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e8"),
        ("Example.Series.S2.2020.1080p", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e9"),
    ]

    ranked_torrents = rtn.batch_rank(torrents)
    assert len(ranked_torrents) == 3
    for torrent in ranked_torrents:
        assert isinstance(torrent, Torrent)
        assert isinstance(torrent.data, ParsedData)
        assert torrent.fetch is True
        assert torrent.rank > 0, f"Rank was {torrent.rank} instead of > 0"
        assert torrent.lev_ratio == 0.0, f"Levenshtein ratio was {torrent.lev_ratio} instead of > 0.0"


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


def test_resolution_ranking(enabled_settings_model, ranking_model):
    test_dict = {
        "4K": 4,
        "2160p": 4,
        "1440p": 4,
        "1080p": 3,
        "720p": 2,
        "576p": -1,
        "480p": -1,
    }

    for key, rank in test_dict.items():
        parsed_data = ParsedData(raw_title=key, parsed_title=key, resolution=[key])
        assert get_rank(parsed_data, enabled_settings_model, ranking_model) == rank, f"{key} resolution should have rank {rank}"
    assert get_rank(ParsedData(raw_title="Other", parsed_title="Other", resolution=["Other"]), enabled_settings_model, ranking_model) == 0, "Other resolution should have rank 0"
    assert get_rank(ParsedData(raw_title="None", parsed_title="None", resolution=[]), enabled_settings_model, ranking_model) == 0, "No resolution should have rank 0"


def test_quality_ranking(enabled_settings_model, ranking_model):
    test_dict = {
        "WEB-DL": 1,
        "Blu-ray": 1,
        "BDRip": 5,
        "BRRip": 0,
        "WEBCap": -1000,
        "Cam": -1000,
        "Telesync": -1000,
        "Telecine": -1000,
        "Screener": -1000,
        "VODRip": -1000,
        "TVRip": -1000,
        "DVD-R": -1000,
    }

    for key, rank in test_dict.items():
        parsed_data = ParsedData(raw_title=key, parsed_title=key, quality=[key])
        assert get_rank(parsed_data, enabled_settings_model, ranking_model) == rank, f"{key} quality should have rank {rank}"
    assert get_rank(ParsedData(raw_title="Other", parsed_title="Other", quality=["Other"]), enabled_settings_model, ranking_model) == 0, "Other quality should have rank 0"
    assert get_rank(ParsedData(raw_title="None", parsed_title="None", quality=[]), enabled_settings_model, ranking_model) == 0, "No quality should have rank 0"


def test_codec_ranking(enabled_settings_model, ranking_model):
    test_dict = {
        "Xvid": -1000,
        "H.263": -1000,
        "VC-1": -1000,
        "MPEG-2": -1000,
        "AV1": 1,
        "H.264": 3,
        "H.265": 0,
        "H.265 Main 10": 0,
        "HEVC": 0,
        "AVC": 0,
    }

    for key, rank in test_dict.items():
        parsed_data = ParsedData(raw_title=key, parsed_title=key, codec=[key])
        assert get_rank(parsed_data, enabled_settings_model, ranking_model) == rank, f"{key} codec should have rank {rank}"
    assert get_rank(ParsedData(raw_title="Other", parsed_title="Other", codec=["Other"]), enabled_settings_model, ranking_model) == 0, "Other codec should have rank 0"
    assert get_rank(ParsedData(raw_title="None", parsed_title="None", codec=[]), enabled_settings_model, ranking_model) == 0, "No codec should have rank 0"


def test_audio_ranking(enabled_settings_model, enabled_ranking_model):
    test_dict = {
        "Dolby TrueHD": 1,
        "Dolby Atmos": 1,
        "Dolby Digital": 1,
        "Dolby Digital EX": 1,
        "Dolby Digital Plus": 1,
        "DTS": 1,
        "DTS-HD": 1,
        "DTS-HD MA": 1,
        "DTS-EX": 1,
        "DTS:X": 1,
        "AAC": 1,
        "AAC-LC": 1,
        "HE-AAC": 1,
        "HE-AAC v2": 1,
        "AC3": 1,
    }

    for key, rank in test_dict.items():
        parsed_data = ParsedData(raw_title=key, parsed_title=key, audio=[key])
        assert get_rank(parsed_data, enabled_settings_model, enabled_ranking_model) == rank, f"{key} audio should have rank {rank}"
    assert get_rank(ParsedData(raw_title="FLAC", parsed_title="FLAC", audio=["FLAC"]), enabled_settings_model, enabled_ranking_model) == -1000, "FLAC audio should have rank -1000"
    assert get_rank(ParsedData(raw_title="OGG", parsed_title="OGG", audio=["OGG"]), enabled_settings_model, enabled_ranking_model) == -1000, "OGG audio should have rank -1000"
    assert get_rank(ParsedData(raw_title="Other", parsed_title="Other", audio=["Other"]), enabled_settings_model, enabled_ranking_model) == 0, "Other audio should have rank 0"
    assert get_rank(ParsedData(raw_title="None", parsed_title="None", audio=[]), enabled_settings_model, enabled_ranking_model) == 0, "No audio should have rank 0"


def test_other_ranks_calculation(enabled_settings_model, ranking_model):
    # Test Valid Data
    rank_8bit = ParsedData(raw_title="8bit", parsed_title="8bit", bitDepth=[8])
    rank_10bit = ParsedData(raw_title="10bit", parsed_title="10bit", bitDepth=[10])
    rank_hdr = ParsedData(raw_title="HDR", parsed_title="HDR", hdr="HDR")
    rank_hdr10 = ParsedData(raw_title="HDR10+", parsed_title="HDR10+", hdr="HDR10+")
    rank_dv = ParsedData(raw_title="DV", parsed_title="DV", hdr="DV")
    rank_complete = ParsedData(raw_title="Complete", parsed_title="Complete", is_complete=True)
    rank_season = ParsedData(raw_title="Season 1", parsed_title="Season 1", season=[1])
    rank_episode = ParsedData(raw_title="Episode", parsed_title="Episode", episode=[1, 2, 3, 4, 5])
    # Test Invalid Data
    rank_none = ParsedData(raw_title="None", parsed_title="None")

    test_dict = {
        "8bit": rank_8bit,
        "10bit": rank_10bit,
        "HDR": rank_hdr,
        "HDR10+": rank_hdr10,
        "DV": rank_dv,
        "Complete": rank_complete,
        "Season": rank_season,
        "Episode": rank_episode,
    }

    for key, data in test_dict.items():
        rank = get_rank(data, enabled_settings_model, ranking_model)
        assert rank > 0, f"{key} data should have positive rank"
    assert get_rank(rank_none, enabled_settings_model, ranking_model) == 0, "No data should have rank 0"


def test_manual_fetch_check_from_user(settings_model, ranking_model):
    rtn = RTN(settings_model, ranking_model, lev_threshold=0.85)
    
    item: Torrent = rtn.rank(
        "marvels.agents.of.s.h.i.e.l.d.s03.1080p.bluray.x264-shortbrehd[rartv]",
        "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7",
        correct_title="Marvel's Agents of S.H.I.E.L.D.",
        remove_trash=True
    )

    assert item.fetch is True, "Fetch should be True"
    assert item.lev_ratio > 0.0, "Levenshtein ratio should be greater than 0.0"