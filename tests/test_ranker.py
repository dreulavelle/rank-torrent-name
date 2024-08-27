import pytest

from RTN import RTN
from RTN.exceptions import GarbageTorrent
from RTN.models import (
    BaseRankingModel,
    DefaultRanking,
    ParsedData,
    SettingsModel,
)
from RTN.parser import Torrent, parse
from RTN.ranker import (
    get_rank,
    calculate_preferred,
    calculate_resolution_rank,
    calculate_audio_rank
)


@pytest.fixture
def ranking_model():
    return DefaultRanking()

@pytest.fixture
def custom_ranking_model():
    return BaseRankingModel(
        uhd=1,
        fhd=1,
        hd=1,
        sd=1,
        av1=1,
        avc=1,
        bluray=1,
        dvd=1,
        hdtv=1,
        hevc=1,
        mpeg=1,
        remux=1,
        vhs=1,
        web=1,
        webdl=1,
        webmux=1,
        xvid=1,
        pdtv=1,
        bdrip=1,
        brrip=1,
        dvdrip=1,
        hdrip=1,
        ppvrip=1,
        tvrip=1,
        uhdrip=1,
        webdlrip=1,
        webrip=1,
        bit_10=1,
        dolby_vision=1,
        hdr=1,
        hdr10plus=1,
        sdr=1,
        aac=1,
        ac3=1,
        atmos=1,
        dolby_digital=1,
        dolby_digital_plus=1,
        dts_lossy=1,
        dts_lossless=1,
        eac3=1,
        flac=1,
        mono=1,
        mp3=1,
        stereo=1,
        surround=1,
        truehd=1,
        three_d=1,
        converted=1,
        documentary=1,
        dubbed=1,
        edition=1,
        hardcoded=1,
        network=1,
        proper=1,
        repack=1,
        retail=1,
        subbed=1,
        upscaled=1,
        cam=1,
        clean_audio=1,
        r5=1,
        screener=1,
        site=1,
        size=1,
        telecine=1,
        telesync=1,
        workprint=1,
    )

@pytest.fixture
def settings_model():
    return SettingsModel()

@pytest.fixture
def custom_settings_model():
    return SettingsModel(
        preferred=["S2"]
    )



@pytest.mark.parametrize("raw_title, expected_fetch", [
    ("The Walking Dead S05E03 720p Remux x264-ASAP[ettv]", False),
    ("The Walking Dead.S05E03.2019.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HEVC.REMUX-JATO", False),
    ("The Walking Dead S05E03 720p x264-ASAP", True),
])
def test_valid_torrent_from_title(settings_model, ranking_model, raw_title, expected_fetch):
    rtn = RTN(settings_model, ranking_model)

    torrent: Torrent = rtn.rank(
        raw_title,
        "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", 
        correct_title="The Walking Dead",
        remove_trash=True
    )

    assert isinstance(torrent, Torrent)
    assert isinstance(torrent.data, ParsedData)
    assert torrent.data.parsed_title == "The Walking Dead", f"Parsed title was {torrent.data.parsed_title} instead of The Walking Dead"
    assert torrent.fetch is expected_fetch, f"Fetch was {torrent.fetch} instead of {expected_fetch}"
    assert torrent.rank != 0, f"Rank was {torrent.rank} instead of 60"
    assert torrent.lev_ratio > 0.0, f"Levenshtein ratio was {torrent.lev_ratio} instead of > 0.0"


@pytest.mark.parametrize("raw_title, infohash, correct_title, exception_type", [
    ("The Walking Dead S05E03 CAM 720p HDTV x264-ASAP[ettv]", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", "The Walking Dead", GarbageTorrent),
    ("c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", None, None, ValueError),  # Missing 2 string arguments
    (None, "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", None, ValueError),  # Missing title
    ("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", None, None, ValueError),  # Missing infohash
    (None, None, None, ValueError),  # Missing title and infohash
    (123, "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", None, TypeError),  # Invalid title type
    ("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", 123, None, TypeError),  # Invalid infohash type
    ("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", "c08a9ee8ce3a5c2c0886", None, TypeError),  # Invalid infohash length
    ("", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", None, ValueError),  # Empty title
])
def test_invalid_torrent_from_title(settings_model, ranking_model, raw_title, infohash, correct_title, exception_type):
    rtn = RTN(settings_model, ranking_model)
    with pytest.raises(exception_type):
        rtn.rank(raw_title, infohash, correct_title=correct_title, remove_trash=True)


def test_rank_calculation_accuracy(settings_model, ranking_model):
    parsed_data = parse("Example.Movie.2020.1080p.BluRay.x264-Example")
    rank = get_rank(parsed_data, settings_model, ranking_model)
    assert rank > 0, f"Expected rank did not match, got {rank}"


@pytest.mark.parametrize("raw_title, expected_rank, parsed_data, exception_type", [
    ("Example.Movie.2020.1080p.BluRay.x264-Example", 1, None, None),
    ("", None, ParsedData(raw_title="", parsed_title="Example Movie"), ValueError),
    (None, None, None, TypeError),  # type: ignore
])
def test_get_rank_validity(settings_model, ranking_model, raw_title, expected_rank, parsed_data, exception_type):
    if exception_type:
        with pytest.raises(exception_type):
            get_rank(parsed_data, settings_model, ranking_model)
    else:
        parsed_data = parse(raw_title)
        rank = get_rank(parsed_data, settings_model, ranking_model)
        assert isinstance(rank, int)
        assert rank > 0


def test_valid_preferred_calculation(custom_settings_model):
    # use calculate_preferred function
    custom_settings_model.preferred = ["S2"]

    parsed_data = ParsedData(
        raw_title="Example.Series.S2.2020.Bluray",
        parsed_title="Example Series",
    )
    # test if preferred is not empty
    rank = calculate_preferred(parsed_data, custom_settings_model)
    assert rank == 10000, f"Expected rank did not match, got {rank}"

    custom_settings_model.preferred = []
    parsed_data = ParsedData(
        raw_title="Example.Movie.2020.1080p-Example",
        parsed_title="Example Movie",
    )
    # test if preferred is empty
    rank = calculate_preferred(parsed_data, custom_settings_model)
    assert rank == 0, f"Expected rank did not match, got {rank}"


def test_preference_handling(settings_model, ranking_model):
    # Test with preferred title with a preference for Season number in title
    # to make sure we can check before-after case. User should be able to set
    # their own preferred patterns dynamically.
    parsed_data = parse("Wonder Woman 1984 (2020) [UHDRemux 2160p DoVi P8 Es-DTSHD AC3 En-AC3")
    rank_with_preference = get_rank(parsed_data, settings_model, ranking_model)
    assert rank_with_preference < 0, "Preferred title should have negative rank (remux)"


def test_resolution_ranking(settings_model, ranking_model):
    test_dict = {
        "4K": 2000,
        "2160p": 2000,
        "1440p": 1000,
        "1080p": 1000,
        "720p": 500,
        "576p": -100,
        "480p": -100,
    }

    for key, rank in test_dict.items():
        parsed_data = ParsedData(raw_title=key, parsed_title=key, resolution=key)
        assert calculate_resolution_rank(parsed_data, settings_model, ranking_model) == rank, f"{key} resolution should have rank {rank}"
    assert calculate_resolution_rank(ParsedData(raw_title="Other", parsed_title="Other", resolution="Other"), settings_model, ranking_model) == 0, "Other resolution should have rank 0"
    assert calculate_resolution_rank(ParsedData(raw_title="None", parsed_title="None", resolution=""), settings_model, ranking_model) == 0, "No resolution should have rank 0"


def test_quality_ranking(settings_model, ranking_model):
    test_dict = {
        "WEB": 150,
        "WEB-DL": 100,
        "BluRay": 100,
        "HDTV": -1000,
        "VHS": -10000,
        "WEBMux": -10000,
        "BluRay REMUX": -1000,
        "REMUX": -1000,
        "WEBRip": 30,
        "WEB-DLRip": -10000,
        "UHDRip": -1000,
        "HDRip": -1000,
        "DVDRip": -1000,
        "BDRip": -1000,
        "BRRip": -1000,
        "VHSRip": -10000,
        "PPVRip": -1000,
        "SATRip": -10000,
        "TVRip": -10000,
        "TeleCine": -10000,
        "TeleSync": -10000,
        "SCR": -10000,
        "R5": -10000,
        "CAM": -10000,
        "PDTV": -10000,
    }

    for key, rank in test_dict.items():
        parsed_data = ParsedData(raw_title=key, parsed_title=key, quality=key)
        assert get_rank(parsed_data, settings_model, ranking_model) == rank, f"{key} quality should have rank {rank}"
    assert get_rank(ParsedData(raw_title="Other", parsed_title="Other", quality="Other"), settings_model, ranking_model) == 0, "Other quality should have rank 0"
    assert get_rank(ParsedData(raw_title="None", parsed_title="None", quality=""), settings_model, ranking_model) == 0, "No quality should have rank 0"


def test_codec_ranking(settings_model, ranking_model):
    test_dict = {
        "avc": 100,
        "hevc": 100,
        "xvid": -10000,
        "av1": 0,
        "mpeg": -100,
    }

    for key, rank in test_dict.items():
        parsed_data = ParsedData(raw_title=key, parsed_title=key, codec=key)
        assert get_rank(parsed_data, settings_model, ranking_model) == rank, f"{key} codec should have rank {rank}"
    assert get_rank(ParsedData(raw_title="Other", parsed_title="Other", codec="Other"), settings_model, ranking_model) == 0, "Other codec should have rank 0"
    assert get_rank(ParsedData(raw_title="None", parsed_title="None", codec=""), settings_model, ranking_model) == 0, "No codec should have rank 0"


def test_audio_ranking(settings_model, custom_ranking_model):
    test_dict = {
        "AAC": 1,
        "AC3": 1,
        "Atmos": 1,
        "Dolby Digital": 1,
        "Dolby Digital Plus": 1,
        "DTS Lossy": 1,
        "DTS Lossless": 1,
        "EAC3": 1,
        "FLAC": 1,
        "MP3": 1,
        "TrueHD": 1,
        "HQ Clean Audio": 1,
    }

    for key, rank in test_dict.items():
        parsed_data = ParsedData(raw_title=key, parsed_title=key, audio=[key])
        assert calculate_audio_rank(parsed_data, settings_model, custom_ranking_model) == rank, f"{key} audio should have rank {rank}"
    assert calculate_audio_rank(ParsedData(raw_title="Other", parsed_title="Other", audio=["Other"]), settings_model, custom_ranking_model) == 0, "Other audio should have rank 0"
    assert calculate_audio_rank(ParsedData(raw_title="None", parsed_title="None", audio=[]), settings_model, custom_ranking_model) == 0, "No audio should have rank 0"


def test_manual_fetch_check_from_user(settings_model, ranking_model):
    rtn = RTN(settings_model, ranking_model)
    
    item: Torrent = rtn.rank(
        "marvels.agents.of.s.h.i.e.l.d.s03.1080p.bluray.x264-shortbrehd[rartv]",
        "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7",
        correct_title="Marvel's Agents of S.H.I.E.L.D."
    )

    assert item.fetch is True, "Fetch should be True"
    assert item.lev_ratio > 0.0, "Levenshtein ratio should be greater than 0.0"