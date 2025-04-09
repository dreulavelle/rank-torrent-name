import pytest

from RTN import RTN, parse
from RTN.exceptions import GarbageTorrent
from RTN.fetch import fetch_resolution
from RTN.models import DefaultRanking, SettingsModel


@pytest.fixture()
def settings_model():
    return SettingsModel()

@pytest.fixture()
def default_ranking():
    return DefaultRanking()


SCRAPED_DATA = [
    # These items will be fetched based on default settings
    {"title": "Game of Thrones S01-S05 1080p 10bit BluRay 6CH x265 HEVC", "fetch": True, "rank": 1},
    {"title": "Game.Of.Thrones.S01-S06.1080p.Bluray.x265.10bit.AAC.7.1.DUAL.Tigole", "fetch": True, "rank": 1},
    {"title": "Game Of Thrones - Season 1 to 6 (Eng Subs) - Mp4 1080p", "fetch": True, "rank": 0},
    {"title": "Game Of Thrones Season 1 S01 Complete (1080p Bluray X265 HEVC AAC 5.1 Joy) [UTR]", "fetch": True, "rank": 1},
    {"title": "Game.of.Thrones.Season.1-8.S01-08.COMPLETE.1080p.BluRay.WEB.x265.10bit.6CH.ReEnc-LUMI", "fetch": True, "rank": 1},
    {"title": "Game of Thrones (2011) 1080p MKV S01E01 Eng NL Subs DMT", "fetch": True, "rank": 0},
    {"title": "Game.of.Thrones.SEASON.01.S01.COMPLETE.1080p.10bit.BluRay.6CH.x265.HEVC-PSA", "fetch": True, "rank": 1},
    {"title": "Game.of.Thrones.S01-S08.COMPLETE.SERIES.REPACK.1080p.Bluray.x265-HiQVE", "fetch": True, "rank": 1},
    {"title": "Game of Thrones (Integrale) MULTi HDLight 1080p HDTV", "fetch": True, "rank": -1},
    {"title": "Game of Thrones - The Iron Anniversary (2021) Season 1 S01 + Extras (1080p HMAX WEB-DL x265 HEVC 10bit AC3 2.0 t3nzin)", "fetch": True, "rank": 1},
    {"title": "Game of Thrones Season 1 to 8 The Complete Collection [NVEnc H265 1080p][AAC 6Ch][English Subs]", "fetch": True, "rank": 1},
    {"title": "Game.of.Thrones.S01.1080p.BluRay.10bit.HEVC-MkvCage Season 1 One", "fetch": True, "rank": 1},
    {"title": "Game of Thrones S01 1080p BluRay-RMZ x264-Belex Dual Audio DTS +", "fetch": True, "rank": 1},
    {"title": "Game of Thrones s01e01 2011 1080p Rifftrax 6ch x265 HEVC", "fetch": True, "rank": 1},
    {"title": "Game of Thrones S01 1080p BluRay H264 AC3 Will1869", "fetch": True, "rank": 1},
    {"title": "Game.of.Thrones.S01.1080p.BluRay.x264-HD4U Season 1 One Complete", "fetch": True, "rank": 1},
    {"title": "Game of Thrones Seasons 1 to 8 The Complete Box Set/Series [English Subs][NVEnc H265 720p][AAC 6Ch]", "fetch": True, "rank": 1},
    {"title": "Game of Thrones - Season 1 - 720p BluRay - x264 - ShAaNiG", "fetch": True, "rank": 1},
    {"title": "Game of Thrones S01E01 720p HDTV x264-CTU [eztv]", "fetch": True, "rank": -1},
    {"title": "Game of Thrones Season 1 S01 720p BluRay x264", "fetch": True, "rank": 1},
    {"title": "Game.of.Thrones.Complete.Series.Season.1.2.3.4.5.6.7.8.x264.720p", "fetch": True, "rank": 1},
    {"title": "Game.of.Thrones.S01.COMPLETE.720p.10bit.BluRay.2CH.x265.HEVC-PSA", "fetch": True, "rank": 1},
    {"title": "Game of Thrones Seasons 1-5 CENSORED", "fetch": True, "rank": 0},
    {"title": "Game.of.Thrones.S01.ITA.ENG.AC3.1080p.H265-BlackEgg", "fetch": True, "rank": 1},
    {"title": "Game.Of.Thrones.Season.1-4.Complete.720p.x264.Arabic-sub", "fetch": True, "rank": 1},
    {"title": "Game of Thrones 1ª a 8ª Temporada Completa [720p-1080p] [BluRay] [DUAL]", "fetch": True, "rank": 1},
    {"title": "Juego De Tronos Temporada-1 Completa 720p Español De Esp", "fetch": True, "rank": 0},
    {"title": "game of thrones 1-4 temporada sub-español", "fetch": True, "rank": 0},
    {"title": "Game of Thrones S01 Complete 720p BluRay x264 Hindi English[MW]", "fetch": True, "rank": 1},
    {"title": "Game of Thrones Temporada 1 Español Latino", "fetch": True, "rank": 0},
    {"title": "Game of Thrones 1ª a 7ª Temporada Completa [720p] [BluRay] [DUAL]", "fetch": True, "rank": 1},
    {"title": "Game of Thrones (2011) Complete [2160p] [HDR] [5.1] [ger eng] [Vio]", "fetch": False, "rank": 1},
    {"title": "Game.of.Thrones.S01.2160p.UHD.BluRay.x265.10bit.HDR.TrueHD.7.1.Atmos-DON[rartv]", "fetch": False, "rank": 1},
    {"title": "Game of Thrones Season 1 (S01) 2160p HDR 5.1 x265 10bit Phun Psyz", "fetch": False, "rank": 1},

    # These items will NOT be fetched based on default settings
    {"title": "Game.of.Thrones.S01-07.BDRip.1080p", "fetch": False, "rank": -1},
    {"title": "Game of Thrones S01-S07 720p 33GB - MkvCage", "fetch": False, "rank": -1},
    {"title": "Game Of Thrones - The Complete Collection (2011-2019) BDRip 1080p", "fetch": False, "rank": -1},
    {"title": "Game.of.Thrones.S01.2160p.DoVi.HDR.BluRay.REMUX.HEVC.DTS-HD.MA.TrueHD.7.1.Atmos-PB69", "fetch": False, "rank": -1},
    {"title": "Game.of.Thrones.S01.2160p.BluRay.REMUX.HEVC.DTS-HD.MA.TrueHD.7.1.Atmos-FGT", "fetch": False, "rank": -1},
    {"title": "Game.of.Thrones.S01.2160p.UHD.BluRay.x265-SCOTLUHD", "fetch": False, "rank": 1},
    {"title": "Game Of Thrones (2011) Season 01 S01 REPACK (2160p BluRay X265 HEVC 10bit AAC 7.1 Joy) [UTR]", "fetch": False, "rank": 1},
    {"title": "Game.Of.Thrones.S01-S04.BluRay.4K.UHD.H265", "fetch": False, "rank": 1},
    {"title": "Game of Thrones S01E01 2160p UHD BluRay x265-SCOTLUHD [eztv]", "fetch": False, "rank": 1},
    {"title": "Game of Thrones - Temporadas Completas (1080p) Acesse o ORIGINAL WWW.BLUDV.TV", "fetch": False, "rank": 0},
    {"title": "Game.of.Thrones.S01.1080p.BluRay.REMUX.AVC.TrueHD.7.1.Atmos-BiZKiT[rartv]", "fetch": False, "rank": -1},
    {"title": "Juego de tronos Temporada 1 completa [BDremux 1080p][DTS 5.1 Castellano-DTS 5.1 Ingles+Subs][ES-EN]", "fetch": False, "rank": -1},
    {"title": "Juego de tronos Temporada 1 [BDremux 1080p][DTS 5.1 Castellano-DTS 5.1 Ingles+Subs][ES-EN]", "fetch": False, "rank": -1},
    {"title": "Il.Trono.Di.Spade.S01E01-10.BDMux.1080p.AC3.ITA.ENG.SUBS.HEVC", "fetch": False, "rank": -1},
    {"title": "Игра престолов / Game of Thrones [S01-08] (2013-2022) BDRip 1080p от Generalfilm | D | P", "fetch": False, "rank": -1},
    {"title": "Игра престолов / Game of Thrones [S01-08] (2011-2019) BDRip 720p | LostFilm", "fetch": False, "rank": -1},
    {"title": "Game of Thrones Season Pack S01 to S08 480p English x264.UNCENSORED", "fetch": False, "rank": 1},
]

@pytest.mark.parametrize("title", [item["title"] for item in SCRAPED_DATA])
def test_scrape_results_with_rank(settings_model, default_ranking, title):
    """Scrape a show from torrentio"""
    data = next(item for item in SCRAPED_DATA if item["title"] == title)
    
    rtn = RTN(settings_model, default_ranking)
    torrent = rtn.rank(
        title,
        "e15ed82226e34aec738cfa691aeb85054df039de",
        correct_title="Game of Thrones",
        remove_trash=False
    )

    assert torrent.fetch == data["fetch"], f"Expected fetch to be {data['fetch']}, got {torrent.fetch}"
    if data["rank"] < 0:
        assert torrent.rank < 0, f"Expected rank to be less than 0, got {torrent.rank}"
    elif data["rank"] > 0:
        assert torrent.rank > 0, f"Expected rank to be greater than 0, got {torrent.rank}"
    else:
        assert torrent.rank == 0, f"Expected rank to be 0, got {torrent.rank}"

@pytest.mark.parametrize(
    "title, expected_hdr",
    [
        ("Game of Thrones S01 1080p HDR", ["HDR"]),
        ("Game of Thrones S01 1080p", [])
    ]
)
def test_hdr(settings_model, title, expected_hdr):
    data = parse(title)
    failed_keys = set()
    fetch_resolution(data, settings_model, failed_keys)
    assert not failed_keys, f"Expected no failed keys for {title}"
    assert data.hdr == expected_hdr, f"Expected {expected_hdr} for {title}, got {data.hdr}"
