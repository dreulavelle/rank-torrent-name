import pytest
from pydantic import ValidationError

from RTN import get_rank, parse
from RTN.exceptions import GarbageTorrent
from RTN.fetch import check_trash
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
    parsett,
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
        "The Simpsons S01E01-E02-E03-E04-E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole",
        "The.Matrix.1999.1080p.BluRay.x264",
        "Inception.2010.720p.BRRip.x264",
        "The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole",
        "The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole",
        "The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole",
        "The Simpsons S01E01E02E03E04E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole",
        "The Simpsons E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole",
        "House MD All Seasons (1-8) 720p Ultra-Compressed",
        "The Avengers (EMH) - S01 E15 - 459 (1080p - BluRay)",
        "[F-D] Fairy Tail Season 1 - 6 + Extras [480P][Dual-Audio]",
        "BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p",
        "Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World",
        "Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]",
        "4-13 Cursed (HD)",
        "Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p BluRay x264 DTS 5.1 -DDR",
        "[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ",
        "Bleach 10º Temporada - 215 ao 220 - [DB-BR]",
        "Naruto Shippuden - 107 - Strange Bedfellows",
        "[224] Shingeki no Kyojin - S03 - Part 1 - 13 [BDRip.1080p.x265.FLAC]",
        "[Erai-raws] Shingeki no Kyojin Season 3 - 11 [1080p][Multiple Subtitle].mkv"
    ]


@pytest.mark.parametrize("test_string, expected", [
    ("The Simpsons S28E21 720p HDTV x264-AVS", [28]),
    ("breaking.bad.s01e01.720p.bluray.x264-reward", [1]),
    ("S011E16.mkv", [11]),
    ("Dragon Ball Super S01 E23 French 1080p HDTV H264-Kesni", [1]),
    ("The Twilight Zone 1985 S01E23a Shadow Play.mp4", [1]),
    ("Mash S10E01b Thats Show Biz Part 2 1080p H.264 (moviesbyrizzo upload).mp4", [10]),
    ("The Twilight Zone 1985 S01E22c The Library.mp4", [1]),
    ("Desperate.Housewives.S0615.400p.WEB-DL.Rus.Eng.avi", [6]),
    ("Doctor.Who.2005.8x11.Dark.Water.720p.HDTV.x264-FoV", [8]),
    ("Orange Is The New Black Season 5 Episodes 1-10 INCOMPLETE (LEAKED)", [5]),
    ("Smallville (1x02 Metamorphosis).avi", [1]),
    ("The.Man.In.The.High.Castle1x01.HDTV.XviD[www.DivxTotaL.com].avi", [1]),
    ("clny.3x11m720p.es[www.planetatorrent.com].mkv", [3]),
    ("Game Of Thrones Complete Season 1,2,3,4,5,6,7 406p mkv + Subs", [1, 2, 3, 4, 5, 6, 7]),
    ("Futurama Season 1 2 3 4 5 6 7 + 4 Movies - threesixtyp", [1, 2, 3, 4, 5, 6, 7]),
    ("Breaking Bad Complete Season 1 , 2 , 3, 4 ,5 ,1080p HEVC", [1, 2, 3, 4, 5]),
    ("True Blood Season 1, 2, 3, 4, 5 & 6 + Extras BDRip TSV", [1, 2, 3, 4, 5, 6]),
    ("How I Met Your Mother Season 1, 2, 3, 4, 5, & 6 + Extras DVDRip", [1, 2, 3, 4, 5, 6]),
    ("The Simpsons Season 20 21 22 23 24 25 26 27 - threesixtyp", [20, 21, 22, 23, 24, 25, 26, 27]),
    ("Perdidos: Lost: Castellano: Temporadas 1 2 3 4 5 6 (Serie Com", [1, 2, 3, 4, 5, 6]),
    ("The Boondocks Season 1, 2 & 3", [1, 2, 3]),
    ("Boondocks, The - Seasons 1 + 2", [1, 2]),
    ("The Boondocks Seasons 1-4 MKV", [1, 2, 3, 4]),
    ("The Expanse Complete Seasons 01 & 02 1080p", [1, 2]),
    ("Friends.Complete.Series.S01-S10.720p.BluRay.2CH.x265.HEVC-PSA", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    ("Stargate Atlantis ALL Seasons - S01 / S02 / S03 / S04 / S05", [1, 2, 3, 4, 5]),
    ("Stargate Atlantis Complete (Season 1 2 3 4 5) 720p HEVC x265", [1, 2, 3, 4, 5]),
    ("Skam.S01-S02-S03.SweSub.720p.WEB-DL.H264", [1, 2, 3]),
    ("Seinfeld S02 Season 2 720p WebRip ReEnc-DeeJayAhmed", [2]),
    ("Seinfeld Season 2 S02 720p AMZN WEBRip x265 HEVC Complete", [2]),
    ("House MD All Seasons (1-8) 720p Ultra-Compressed", [1, 2, 3, 4, 5, 6, 7, 8]),
    ("Teen Titans Season 1-5", [1, 2, 3, 4, 5]),
    ("Game Of Thrones - Season 1 to 6 (Eng Subs)", [1, 2, 3, 4, 5, 6]),
    ("Travelers - Seasons 1 and 2 - Mp4 x264 AC3 1080p", [1, 2]),
    ("Naruto Shippuden Season 1:11", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
    ("South Park Complete Seasons 1: 11", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
    ("24 Season 1-8 Complete with Subtitles", [1, 2, 3, 4, 5, 6, 7, 8]),
    ("One Punch Man 01 - 12 Season 1 Complete [720p] [Eng Subs] [Xerxe:16", [1]),
    ("[5.01] Weight Loss.avi", [5]),
    ("Dragon Ball [5.134] Preliminary Peril.mp4", [5]),
    ("Bron - S4 - 720P - SweSub.mp4", [4]),
    ("Mad Men S02 Season 2 720p 5.1Ch BluRay ReEnc-DeeJayAhmed", [2]),
    ("Friends S04 Season 4 1080p 5.1Ch BluRay ReEnc-DeeJayAhmed", [4]),
    ("Doctor Who S01--S07--Complete with holiday episodes", [1, 2, 3, 4, 5, 6, 7]),
    ("My Little Pony FiM - 6.01 - No Second Prances.mkv", [6]),
    ("Desperate Housewives - Episode 1.22 - Goodbye for now.avi", [1]),
    ("All of Us Are Dead . 2022 . S01 EP #1.2.mkv", [1]),
    ("Empty Nest Season 1 (1988 - 89) fiveofseven", [1]),
    ("Game of Thrones / Сезон: 1-8 / Серии: 1-73 из 73 [2011-2019, США, BDRip 1080p] MVO (LostFilm)", [1, 2, 3, 4, 5, 6, 7, 8]),
    ("Друзья / Friends / Сезон: 1, 2 / Серии: 1-24 из 24 [1994-1999, США, BDRip 720p] MVO", [1, 2]),
    ("Друзья / Friends / Сезон: 1 / Серии: 1-24 из 24 [1994-1995, США, BDRip 720p] MVO + Original + Sub (Rus, Eng)", [1]),
    ("Сезон 5/Серия 11.mkv", [5]),
    ("Разрушители легенд. MythBusters. Сезон 15. Эпизод 09. Скрытая угроза (2015).avi", [15]),
    ("Леди Баг и Супер-Кот – Сезон 3, Эпизод 21 – Кукловод 2 [1080p].mkv", [3]),
    ("Проклятие острова ОУК_ 5-й сезон 09-я серия_ Прорыв Дэна.avi", [5]),
    ("2 сезон 24 серия.avi", [2]),
    ("3 сезон", [3]),
    ("2. Discovery-Kak_ustroena_Vselennaya.(2.sezon_8.serii.iz.8).2012.XviD.HDTVRip.Krasnodarka", [2]),
    ("Otchayannie.domochozyaiki.(8.sez.21.ser.iz.23).2012.XviD.HDTVRip.avi", [8]),
    ("Интерны. Сезон №9. Серия №180.avi", [9]),
    ("Discovery. Парни с Юкона / Yokon Men [06х01-08] (2017) HDTVRip от GeneralFilm | P1", [6]),
    ("Zvezdnie.Voiny.Voina.Klonov.3.sezon.22.seria.iz.22.XviD.HDRip.avi", [3]),
    ("2-06. Девичья сила.mkv", [2]),
    ("4-13 Cursed (HD).m4v", [4]),
    ("Доктор Хаус 03-20.mkv", [3]),
    ("Комиссар Рекс 11-13.avi", [11]),
    ("13-13-13 2013 DVDrip x264 AAC-MiLLENiUM", []),
    ("MARATHON EPISODES/Orphan Black S3 Eps.05-08.mp4", [3]),
    ("Once Upon a Time [S01-07] (2011-2017) WEB-DLRip by Generalfilm", [1, 2, 3, 4, 5, 6, 7]),
    ("[F-D] Fairy Tail Season 1 -6 + Extras [480P][Dual-Audio]", [1, 2, 3, 4, 5, 6]),
    ("Coupling Season 1 - 4 Complete DVDRip - x264 - MKV by RiddlerA", [1, 2, 3, 4]),
    ("[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ", [4]),
    ("Tokyo Ghoul Root A - 07 [S2-07] [Eng Sub] 480p [email protected]", [2]),
    ("Ace of the Diamond: 1st Season", [1]),
    ("Ace of the Diamond: 2nd Season", [2]),
    ("Adventure Time 10 th season", [10]),
    ("Kyoukai no Rinne (TV) 3rd Season - 23 [1080p]", [3]),
    ("[Erai-raws] Granblue Fantasy The Animation Season 2 - 08 [1080p][Multiple Subtitle].mkv", [2]),
    ("The Nile Egypts Great River with Bettany Hughes Series 1 4of4 10", [1]),
    ("Teen Wolf - 04ª Temporada 720p", [4]),
    ("Vikings 3 Temporada 720p", [3]),
    ("Eu, a Patroa e as Crianças  4° Temporada Completa - HDTV - Dublado", [4]),
    ("Merl - Temporada 1", [1]),
    ("Elementar 3º Temporada Dublado", [3]),
    ("Beavis and Butt-Head - 1a. Temporada", [1]),
    ("3Âº Temporada Bob esponja Pt-Br", [3]),
    ("Juego de Tronos - Temp.2 [ALTA DEFINICION 720p][Cap.209][Spanish].mkv", [2]),
    ("Los Simpsons Temp 7 DVDrip Espanol De Espana", [7]),
    ("The Walking Dead [Temporadas 1 & 2 Completas Em HDTV E Legena", [1, 2]),
    ("My Little Pony - A Amizade é Mágica - T02E22.mp4", [2]),
    ("30 M0N3D4S ESP T01XE08.mkv", [1]),
    ("Sons of Anarchy Sn4 Ep14 HD-TV - To Be, Act 2, By Cool Release", [4]),
    ("[FFA] Kiratto Pri☆chan Season 3 - 11 [1080p][HEVC].mkv", [3]),
    ("[Erai-raws] Granblue Fantasy The Animation Season 2 - 10 [1080p][Multiple Subtitle].mkv", [2]),
    ("[SCY] Attack on Titan Season 3 - 11 (BD 1080p Hi10 FLAC) [1FA13150].mkv", [3]),
    ("DARKER THAN BLACK - S00E04 - Darker Than Black Gaiden OVA 3.mkv", [0]),
    ("Seizoen 22 - Zon & Maan Ultra Legendes/afl.18 Je ogen op de bal houden!.mp4", [22]),
    ("Ranma-12-86.mp4", []),
    ("[Erai-raws] Shingeki no Kyojin Season 3 - 11 [1080p][Multiple Subtitle].mkv", [3]),

    # From episode parsing, these are not supposed to have seasons either.
    ("523 23.mp4", []),
    ("Chernobyl E02 1 23 45.mp4", []),
    ("Watch Gary And His Demons Episode 10 - 0.00.07-0.11.02.mp4", []),
    ("wwf.raw.is.war.18.09.00.avi", []),
])
def test_extract_seasons(test_string, expected):
    results = parsett(test_string)
    assert results["seasons"] == expected, f"Failed for {test_string}"

@pytest.mark.parametrize("test_string, expected_episode", [
    # Mine
    ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1]),
    ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1, 2]),
    ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1, 2]),
    ("The Simpsons S01E01-E02-E03-E04-E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1, 2, 3, 4, 5]),
    ("The Simpsons S01E01E02E03E04E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1, 2, 3, 4, 5]),
    ("The Simpsons E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", list(range(1, 201))),
    ("House MD All Seasons (1-8) 720p Ultra-Compressed", []),
    ("The Avengers (EMH) - S01 E15 - 459 (1080p - BluRay)", [15]),
    ("Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]", [5]),
    ("4-13 Cursed (HD)", [13]),
    ("Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World", [2]),
    ("Bleach 10º Temporada - 215 ao 220 - [DB-BR]", [215, 216, 217, 218, 219, 220]),
    ("Naruto Shippuden - 107 - Strange Bedfellows", [107]),
    ("[224] Shingeki no Kyojin - S03 - Part 1 - 13 [BDRip.1080p.x265.FLAC]", [13]),
    ("[Erai-raws] Shingeki no Kyojin Season 3 - 11 [1080p][Multiple Subtitle].mkv", [11]),
    ("Joker.2019.PROPER.mHD.10Bits.1080p.BluRay.DD5.1.x265-TMd.mkv", []),
    # PTT
    ("The Simpsons S28E21 720p HDTV x264-AVS", [21]),
    ("breaking.bad.s01e01.720p.bluray.x264-reward", [1]),
    ("Dragon Ball Super S01 E23 French 1080p HDTV H264-Kesni", [23]),
    ("The.Witcher.S01.07.2019.Dub.AVC.ExKinoRay.mkv", [7]),
    ("Vikings.s02.09.AVC.tahiy.mkv", [9]),
    ("The Twilight Zone 1985 S01E23a Shadow Play.mp4", [23]),
    ("Desperate_housewives_S03E02Le malheur aime la compagnie.mkv", [2]),
    ("Mash S10E01b Thats Show Biz Part 2 1080p H.264 (moviesbyrizzo upload).mp4", [1]),
    ("The Twilight Zone 1985 S01E22c The Library.mp4", [22]),
    ("Desperate.Housewives.S0615.400p.WEB-DL.Rus.Eng.avi", [15]),
    ("Doctor.Who.2005.8x11.Dark.Water.720p.HDTV.x264-FoV", [11]),
    ("Anubis saison 01 episode 38 tvrip FR", [38]),
    ("Le Monde Incroyable de Gumball - Saison 5 Ep 14 - L'extérieur", [14]),
    ("Smallville (1x02 Metamorphosis).avi", [2]),
    ("The.Man.In.The.High.Castle1x01.HDTV.XviD[www.DivxTotaL.com].avi", [1]),
    ("clny.3x11m720p.es[www.planetatorrent.com].mkv", [11]),
    ("Friends.S07E20.The.One.With.Rachel's.Big.Kiss.720p.BluRay.2CH.x265.HEVC-PSA.mkv", [20]),
    ("Friends - [8x18] - The One In Massapequa.mkv", [18]),
    ("Friends - [7x23-24] - The One with Monica and Chandler's Wedding + Audio Commentary.mkv", [23, 24]),
    ("Yu-Gi-Oh 3x089 - Awakening of Evil (Part 4).avi", [89]),
    ("611-612 - Desperate Measures, Means & Ends.mp4", [611, 612]),
    ("[Final8]Suisei no Gargantia - 05 (BD 10-bit 1920x1080 x264 FLAC)[E0B15ACF].mkv", [5]),
    ("Orange Is The New Black Season 5 Episodes 1-10 INCOMPLETE (LEAKED)", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    ("Vikings.Season.05.Ep(01-10).720p.WebRip.2Ch.x265.PSA", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    ("[TBox] Dragon Ball Z Full 1-291(Subbed Jap Vers)", list(range(1, 292))),
    ("Marvel's.Agents.of.S.H.I.E.L.D.S02E01-03.Shadows.1080p.WEB-DL.DD5.1", [1, 2, 3]),
    ("Naruto Shippuden Ep 107 - Strange Bedfellows.mkv", [107]),
    ("Naruto Shippuden - 107 - Strange Bedfellows.mkv", [107]),
    ("[AnimeRG] Naruto Shippuden - 107 [720p] [x265] [pseudo].mkv", [107]),
    ("Naruto Shippuuden - 006-007.mkv", [6, 7]),
    ("321 - Family Guy Viewer Mail #1.avi", [321]),
    ("512 - Airport '07.avi", [512]),
    ("102 - The Invitation.avi", [102]),
    ("02 The Invitation.mp4", [2]),
    ("004 - Male Unbonding - [DVD].avi", [4]),
    ("The Amazing World of Gumball - 103, 104 - The Third - The Debt.mkv", [103, 104]),
    ("The Amazing World of Gumball - 103 - The End - The Dress (720p.x264.ac3-5.1) [449].mkv", [103]),
    ("The Amazing World of Gumball - 107a - The Mystery (720p.x264.ac3-5.1) [449].mkv", [107]),
    ("The Amazing World of Gumball - 107b - The Mystery (720p.x264.ac3-5.1) [449].mkv", [107]),
    ("[5.01] Weight Loss.avi", [1]),
    ("Dragon Ball [5.134] Preliminary Peril.mp4", [134]),
    ("S01 - E03 - Fifty-Fifty.mkv", [3]),
    ("The Office S07E25+E26 Search Committee.mp4", [25, 26]),
    ("[animeawake] Naruto Shippuden - 124 - Art_2.mkv", [124]),
    ("[animeawake] Naruto Shippuden - 072 - The Quietly Approaching Threat_2.mkv", [72]),
    ("[animeawake] Naruto Shippuden - 120 - Kakashi Chronicles. Boys' Life on the Battlefield. Part 2.mkv", [120]),
    ("Supernatural - S03E01 - 720p BluRay x264-Belex - Dual Audio + Legenda.mkv", [1]),
    ("[F-D] Fairy Tail Season 1 -6 + Extras [480P][Dual-Audio]", []),
    ("House MD All Seasons (1-8) 720p Ultra-Compressed", []),
    ("Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p", []),
    ("09 Movie - Dragon Ball Z - Bojack Unbound", []),
    ("24 - S01xE03.mp4", [3]),
    ("24 - S01E04 - x264 - dilpill.mkv", [4]),
    ("24.Legacy.S01E05.720p.HEVC.x265-MeGusta", [5]),
    ("[F-D] Fairy.Tail.-.004v2.-. [480P][Dual-Audio].mkv", [4]),
    ("[Exiled-Destiny]_Tokyo_Underground_Ep02v2_(41858470).mkv", [2]),
    ("[a-s]_fairy_tail_-_003_-_infiltrate_the_everlue_mansion__rs2_[1080p_bd-rip][4CB16872].mkv", [3]),
    ("Food Wars! Shokugeki No Souma S4 - 11 (1080p)(HEVC x265 10bit)", [11]),
    ("Dragon Ball Super S05E53 - Ep.129.mkv", [53]),
    ("DShaun.Micallefs.MAD.AS.HELL.S10E03.576p.x642-YADNUM.mkv", [3]),
    ("The Avengers (EMH) - S01 E15 - 459 (1080p - BluRay).mp4", [15]),
    ("My Little Pony FiM - 6.01 - No Second Prances.mkv", [1]),
    ("Desperate Housewives - Episode 1.22 - Goodbye for now.avi", [22]),
    ("All of Us Are Dead . 2022 . S01 EP #1.2.mkv", [2]),
    ("Mob Psycho 100 - 09 [1080p].mkv", [9]),
    ("3-Nen D-Gumi Glass no Kamen - 13 [480p]", [13]),
    ("BBC Indian Ocean with Simon Reeve 5of6 Sri Lanka to Bangladesh.avi", [5]),
    ("Witches Of Salem - 2Of4 - Road To Hell - Gr.mkv", [2]),
    ("Das Boot Miniseries Original Uncut-Reevel Cd2 Of 3.avi", [2]),
    ("Stargate Universe S01E01E02E03.mp4", [1, 2, 3]),
    ("Stargate Universe S01E01-E02-E03.mp4", [1, 2, 3]),
    ("MARATHON EPISODES/Orphan Black S3 Eps.05-08.mp4", [5, 6, 7, 8]),
    ("Pokemon Black & White E10 - E17 [CW] AVI", [10, 11, 12, 13, 14, 15, 16, 17]),
    ("Pokémon.S01E01-E04.SWEDISH.VHSRip.XviD-aka", [1, 2, 3, 4]),
    ("[HorribleSubs] White Album 2 - 06 [1080p].mkv", [6]),
    ("Mob.Psycho.100.II.E10.720p.WEB.x264-URANiME.mkv", [10]),
    ("E5.mkv", [5]),
    ("[OMDA] Bleach - 002 (480p x264 AAC) [rich_jc].mkv", [2]),
    ("[ACX]El_Cazador_de_la_Bruja_-_19_-_A_Man_Who_Protects_[SSJ_Saiyan_Elite]_[9E199846].mkv", [19]),
    ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", [1, 2, 3, 4, 5, 6, 7, 8]),
    ("Мистер Робот / Mr. Robot / Сезон: 2 / Серии: 1-5 (12) [2016, США, WEBRip 1080p] MVO", [1, 2, 3, 4, 5]),
    ("Викинги / Vikings / Сезон: 5 / Серии: 1 [2017, WEB-DL 1080p] MVO", [1]),
    ("Викинги / Vikings / Сезон: 5 / Серии: 1 из 20 [2017, WEB-DL 1080p] MVO", [1]),
    ("Prehistoric park.3iz6.Supercroc.DVDRip.Xvid.avi", [3]),
    ("Меч (05 сер.) - webrip1080p.mkv", [5]),
    ("Серия 11.mkv", [11]),
    ("Разрушители легенд. MythBusters. Сезон 15. Эпизод 09. Скрытая угроза (2015).avi", [9]),
    ("Леди Баг и Супер-Кот – Сезон 3, Эпизод 21 – Кукловод 2 [1080p].mkv", [21]),
    ("Проклятие острова ОУК_ 5-й сезон 09-я серия_ Прорыв Дэна.avi", [9]),
    ("Интерны. Сезон №9. Серия №180.avi", [180]),
    ("Tajny.sledstviya-20.01.serya.WEB-DL.(1080p).by.lunkin.mkv", [1]),
    ("Zvezdnie.Voiny.Voina.Klonov.3.sezon.22.seria.iz.22.XviD.HDRip.avi", [22]),
    ("Otchayannie.domochozyaiki.(8.sez.21.ser.iz.23).2012.XviD.HDTVRip.avi", [21]),
    ("MosGaz.(08.seriya).2012.WEB-DLRip(AVC).ExKinoRay.mkv", [8]),
    ("Tajny.sledstvija.(2.sezon.12.serija.iz.12).2002.XviD.DVDRip.avi", [12]),
    ("Discovery. Парни с Юкона / Yokon Men [06х01-08] (2017) HDTVRip от GeneralFilm | P1", [1, 2, 3, 4, 5, 6, 7, 8]),
    ("2-06. Девичья сила.mkv", [6]),
    ("4-13 Cursed (HD).m4v", [13]),
    ("The Ed Show 10-19-12.mp4", []),
    ("Hogan's Heroes - 516 - Get Fit or Go Flight - 1-09-70.divx", [516]),
    ("Доктор Хаус 03-20.mkv", [20]),
    ("Комиссар Рекс 11-13.avi", [13]),
    ("Kyoukai no Rinne (TV) 3rd Season - 23 [1080p]", [23]),
    ("[224] Shingeki no Kyojin - S03 - Part 1 -  13 [BDRip.1080p.x265.FLAC].mkv", [13]),
    ("El Chema Temporada 1 Capitulo 25", [25]),
    ("Juego de Tronos - Temp.2 [ALTA DEFINICION 720p][Cap.209][Spanish].mkv", [209]),
    ("Blue Bloods - Temporada 11 [HDTV 720p][Cap.1103][AC3 5.1 Castellano][www.PCTmix.com].mkv", [1103]),
    ("Mazinger-Z-Cap-52.avi", [52]),
    ("Yu-Gi-Oh! ZEXAL Temporada 1 Episodio 009 Dual Latino e Inglés [B3B4970E].mkv", [9]),
    ("Bleach 10º Temporada - 215 ao 220 - [DB-BR]", [215, 216, 217, 218, 219, 220]),
    ("My Little Pony - A Amizade é Mágica - T02E22.mp4", [22]),
    ("30 M0N3D4S ESP T01XE08.mkv", [8]),
    ("[CBM]_Medaka_Box_-_11_-_This_Is_the_End!!_[720p]_[436E0E90].mkv", [11]),
    ("[CBM]_Medaka_Box_-_11_-_This_Is_the_End!!_[720p]_[436E0E90]", [11]),
    ("(Hi10)_Re_Zero_Shin_Henshuu-ban_-_02v2_(720p)_(DDY)_(72006E34).mkv", [2]),
    ("22-7 (Season 1) (1080p)(HEVC x265 10bit)(Eng-Subs)-Judas[TGx] ⭐", []),
    ("[Erai-raws] Carole and Tuesday - 01 ~ 12 [1080p][Multiple Subtitle]", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
    ("[Erai-raws] 3D Kanojo - Real Girl 2nd Season - 01 ~ 12 [720p]", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
    ("[FFA] Koi to Producer: EVOL×LOVE - 01 - 12 [1080p][HEVC][AAC]", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
    ("[BenjiD] Quan Zhi Gao Shou (The King’s Avatar) / Full-Time Master S01 (01 - 12) [1080p x265] [Soft sub] V2", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
    ("[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ", [24]),
    ("Tokyo Ghoul Root A - 07 [S2-07] [Eng Sub] 480p [email protected]", [7]),
    ("black-ish.S05E02.1080p..x265.10bit.EAC3.6.0-Qman[UTR].mkv", [2]),
    ("[Eng Sub] Rebirth Ep #36 [8CF3ADFA].mkv", [36]),
    ("[92 Impatient Eilas & Miyafuji] Strike Witches - Road to Berlin - 01 [1080p][BCDFF6A2].mkv", [1]),
    ("[224] Darling in the FranXX - 14 [BDRip.1080p.x265.FLAC].mkv", [14]),
    ("[Erai-raws] Granblue Fantasy The Animation Season 2 - 10 [1080p][Multiple Subtitle].mkv", [10]),
    ("[Erai-raws] Shingeki no Kyojin Season 3 - 11 [1080p][Multiple Subtitle].mkv", [11]),
    ("DARKER THAN BLACK - S00E00.mkv", [0]),
    ("[Erai-raws] 22-7 - 11 .mkv", [11]),
    ("[Golumpa] Star Blazers 2202 - 22 (Uchuu Senkan Yamato 2022) [FuniDub 1080p x264 AAC] [A24B89C8].mkv", [22]),
    ("[SubsPlease] Digimon Adventure (2020) - 35 (720p) [4E7BA28A].mkv", [35]),
    ("[KH] Sword Art Online II - 14.5 - Debriefing.mkv", [14]),
    ("[SSA] Detective Conan - 1001 [720p].mkv", [1001]),
    ("Pwer-04_05.avi", [5]),
    ("SupNat-11_06.avi", [6]),
    ("office_03_19.avi", [19]),
    ("Spergrl-2016-02_04.avi", [4]),
    ("Iron-Fist-2017-01_13-F.avi", [13]),
    ("Lgds.of.Tmrow-02_17.F.avi", [17]),
    ("Ozk.02.09.avi", [9]),
    ("Ozk.02.10.F.avi", [10]),
    ("Cestovatelé_S02E04_11_27.mkv", [4]),
    ("S03E13_91.avi", [13]),
    ("wwe.nxt.uk.11.26.mkv", [26]),
    ("Chernobyl.S01E01.1.23.45.mkv", [1]),
    ("The.Witcher.S01.07.mp4", [7]),
    ("Breaking Bad S02 03.mkv", [3]),
    ("NCIS Season 11 01.mp4", [1]),
    ("Top Gear - 3x05 - 2003.11.23.avi", [5]),
    ("[KTKJ]_[BLEACH]_[DVDRIP]_[116]_[x264_640x480_aac].mkv", [116]),
    ("[GM-Team][国漫][绝代双骄][Legendary Twins][2022][08][HEVC][GB][4K].mp4", [8]),
    # ("8-6 2006.07.16.avi", [6]),   # This is wrong. It should be [6] but instead gets [8]
    ("523 23.mp4", [523]),
    ("Chernobyl E02 1 23 45.mp4", [2]),
    ("Watch Gary And His Demons Episode 10 - 0.00.07-0.11.02.mp4", [10]),
    ("wwf.raw.is.war.18.09.00.avi", []),
])
def test_extract_episodes(test_string, expected_episode):
    results = parsett(test_string)
    assert results["episodes"] == expected_episode, f"Failed for {test_string}"

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
    parsed_results = batch_parse(test_titles, remove_trash=False, chunk_size=50)
    assert len(parsed_results) == len(test_titles)
    for parsed, title in zip(parsed_results, test_titles):
        assert isinstance(parsed, ParsedData)
        assert parsed.raw_title == title

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
        ("Naruto Shippuden - 107 - Strange Bedfellows", [107]),
        ("[224] Shingeki no Kyojin - S03 - Part 1 - 13 [BDRip1080p.x265.FLAC]", [13]),

        # Looks like it doesn't handle hyphens very well in the episode part. It's not a big deal,
        # as it's not a common practice to use hypens in the episode part. Mostly seen in Anime.
        # I did run tests and I was still able to scrape for Naruto, which is a huge win as its always been a tough one!
        ("[Erai-raws] Shingeki no Kyojin Season 3 - 11 [1080p][Multiple Subtitle].mkv", [11]),  # Incorrect, should of been:  [11]

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
    with pytest.raises(GarbageTorrent):
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
    with pytest.raises(ValueError):
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


def test_get_correct_episodes():
    test_cases = [
        ("Yu-Gi-Oh! Zexal - 087 - Dual Duel, Part 1.mkv", [87]),
        ("Yu-Gi-Oh! Zexal - 088 - Dual Duel, Part 2.mkv", [88]),
        ("Yu-Gi-Oh! Zexal - 089 - Darkness Dawns.mkv", [89]),
        ("Yu-Gi-Oh! Zexal - 090 - You Give Love a Bot Name.mkv", [90]),
        ("Yu-Gi-Oh! Zexal - 091 - Take a Chance.mkv", [91]),
        ("Yu-Gi-Oh! Zexal - 092 - An Imperfect Couple, Part 1.mkv", [92]),
        ("Yu-Gi-Oh! Zexal - 093 - An Imperfect Couple, Part 2.mkv", [93]),
        ("Yu-Gi-Oh! Zexal - 094 - Enter Vector.mkv", [94]),
    ]

    # Test RTN
    for test_string, expected in test_cases:
        data = parse(test_string, remove_trash=False)
        assert data.episode == expected, f"Failed for '{test_string}' with expected {expected}"

    # Test PTN
    from PTN import parse as ptn_parse
    for test_string, expected in test_cases:
        data = ptn_parse(test_string, coherent_types=True)
        assert data.get("episode") == expected, f"Failed for '{test_string}' with expected {expected}"

    # Test PTT
    # TODO: Add PTT

def test_trash_coverage():
    # Test the coverage of the trash patterns
    test_cases = [
        ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
        ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
        ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
        ("The Simpsons S01E01-E02-E03-E04-E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
        ("The Simpsons S01E01E02E03E04E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
        ("The Simpsons E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", False),
        ("House MD All Seasons (1-8) 720p Ultra-Compressed", False),
        ("The Avengers (EMH) - S01 E15 - 459 (1080p - BluRay)", False),
        ("Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World", False),
        ("Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]", True), # XviD
        ("4-13 Cursed (HD)", False),
        ("Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p BluRay x264 DTS 5.1 -DDR", False),
        ("[F-D] Fairy Tail Season 1 - 6 + Extras [480P][Dual-Audio]", False),
        ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", True),  # WEB-DLRip
        ("[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ", False),
        ("Bleach 10º Temporada - 215 ao 220 - [DB-BR]", False),
        ("Naruto Shippuden - 107 - Strange Bedfellows", False),
        ("[224] Shingeki no Kyogin - S03 - Part 1 - 13 [BDRip.1080p.x265.FLAC]", False),
        ("[Erai-raws] Shingeki no Kyogin Season 3 - 11 [1080p][Multiple Subtitle]", False),
    ]

    for test_string, expected in test_cases:
        assert check_trash(test_string) == expected, f"Failed for '{test_string}' with expected {expected}"


def test_rtn_default_parse(settings_model, rank_model):
    raw_title = "Ходячие мертвецы: Выжившие / The Walking Dead: The Ones Who Live [01x01-03 из 06] (2024) WEB-DL 1080p от NewComers | P"
    rtn = RTN(settings_model, rank_model)

    # with pytest.raises(GarbageTorrent):
    #     assert rtn.rank(raw_title=raw_title, infohash="c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", correct_title="The Walking Dead", remove_trash=True)

    torrent = rtn.rank(raw_title=raw_title, infohash="c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", correct_title="The Walking Dead", remove_trash=False)
    assert torrent.raw_title == raw_title
    assert torrent.data.type == "show"
    assert torrent.lev_ratio > 0.0
    assert torrent.rank > 0
    assert torrent.data.season == [1]
    assert torrent.data.episode == [1, 2, 3]
    assert torrent.data.resolution == ["1080p"]
    assert torrent.data.quality == ["WEB-DL"]
    assert torrent.data.language == []
    assert torrent.data.subtitles == []
    assert torrent.data.audio == []
    assert torrent.data.codec == []
    assert torrent.data.bitDepth == []
    assert torrent.data.hdr == ""


def test_metadata_mapping_issue_in_kc():
    test_cases = [
        ("3.10.to.Yuma.2007.1080p.BluRay.x264.DTS-SWTYBLZ.mkv", [], []),
        ("30.Minutes.or.Less.2011.1080p.BluRay.X264-SECTOR7.mkv", [], []),
        ("Alien.Covenant.2017.1080p.BluRay.x264-SPARKS[EtHD].mkv", [], []),
        ("Alien.1979.REMASTERED.THEATRICAL.1080p.BluRay.x264.DTS-SWTYBLZ.mkv", [], []),
        ("The Steve Harvey Show - S02E07 - When the Funk Hits the Rib Tips.mkv", [2], [7]),
        ("Fantastic.Beasts.The.Crimes.Of.Grindelwald.2018.4K.HDR.2160p.BDRip Ita Eng x265-NAHOM.mkv", [], [])
    ]

    for test_string, expected_season, expected_episode in test_cases:
        items = parse(test_string, False)
        assert isinstance(items, ParsedData), f"Failed for '{test_string}', expected ParsedData object"
        assert items.season == expected_season, f"Failed for '{test_string}' with expected {expected_season}"
        assert items.episode == expected_episode, f"Failed for '{test_string}' with expected {expected_episode}"


def test_fix_using_constant_instantiation_of_rtn():
    test_cases = [
        ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1], [1]),
        ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1], [1, 2]),
        ("House MD All Seasons (1-8) 720p Ultra-Compressed", [1, 2, 3, 4, 5, 6, 7, 8], []),
        ("The Avengers (EMH) - S01 E15 - 459 (1080p - BluRay)", [1], [15]),
        ("Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World", [], [2]),
        ("Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]", [6], [5]),
        ("4-13 Cursed (HD)", [4], [13]),
    ]

    for test_string, expected_season, expected_episode in test_cases:
        item = parse(test_string, False)
        assert item.season == expected_season, f"Failed for '{test_string}' with expected {expected_season} season"
        assert item.episode == expected_episode, f"Failed for '{test_string}' with expected {expected_episode} episode"
        assert item.year == 0, f"Failed for '{test_string}' with expected 0"


def test_best_season_parser():
    test_cases = [
        ("Archer.S02.1080p.BluRay.DTSMA.AVC.Remux", [2]),
        ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", [1]),
        ("[F-D] Fairy Tail Season 1 - 6 + Extras [480P][Dual-Audio]", [1, 2, 3, 4, 5, 6]),
        ("House MD All Seasons (1-8) 720p Ultra-Compressed", [1, 2, 3, 4, 5, 6, 7, 8]),
        ("Bleach 10º Temporada - 215 ao 220 - [DB-BR]", [10]),
        ("Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]", [6]),
        ("4-13 Cursed (HD)", [4]),
        ("Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p BluRay x264 DTS 5.1 -DDR", []), # Movie
        ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", [6]),
        ("[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ", [4]),
    ]

    for test_string, expected_season in test_cases:
        item = parse(test_string, False)
        assert item.season == expected_season, f"Failed for '{test_string}' with expected {expected_season} season"


def test_output_on_parse(settings_model, rank_model):
    raw_title = "The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole"

    ptn_data = parse(raw_title, remove_trash=False)

    assert ptn_data.raw_title == raw_title
    assert ptn_data.parsed_title == "The Simpsons"
    assert ptn_data.year == 0
    assert ptn_data.resolution == ["1080p"]
    assert ptn_data.quality == ["Blu-ray"]
    assert ptn_data.season == [1]
    assert ptn_data.episode == [1]
    assert ptn_data.codec == ["H.265"]
    assert ptn_data.audio == ["AAC 5.1"]
    assert ptn_data.subtitles == []
    assert ptn_data.language == []
    assert ptn_data.bitDepth == [10]
    assert ptn_data.hdr == ""

    rtn = RTN(settings_model, rank_model)
    rank_data = rtn.rank(raw_title, "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7", "The Simpsons", remove_trash=False)
    
    assert rank_data.raw_title == raw_title
    assert rank_data.data.raw_title == raw_title
    assert rank_data.data.parsed_title == "The Simpsons"
    assert rank_data.data.year == 0
    assert rank_data.data.resolution == ["1080p"]
    assert rank_data.data.quality == ["Blu-ray"]
    assert rank_data.data.season == [1]
    assert rank_data.data.episode == [1]
    assert rank_data.data.codec == ["H.265"]
    assert rank_data.data.audio == ["AAC 5.1"]
    assert rank_data.data.subtitles == []
    assert rank_data.data.language == []
    assert rank_data.data.bitDepth == [10]


@pytest.mark.parametrize("test_string, expected_title", [
    ("The Simpsons S01E01 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "The Simpsons"),
    ("The Simpsons S01E01E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "The Simpsons"),
    ("The Simpsons S01E01-E02 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "The Simpsons"),
    ("The Simpsons S01E01-E02-E03-E04-E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "The Simpsons"),
    ("The Simpsons S01E01E02E03E04E05 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "The Simpsons"),
    ("The Simpsons E1-200 1080p BluRay x265 HEVC 10bit AAC 5.1 Tigole", "The Simpsons"),
    ("House MD All Seasons (1-8) 720p Ultra-Compressed", "House MD"),
    ("The Avengers (EMH) - S01 E15 - 459 (1080p - BluRay)", "The Avengers"),
    ("Witches Of Salem - 2Of4 - Road To Hell - Great Mysteries Of The World", "Witches Of Salem"),
    ("Lost.[Perdidos].6x05.HDTV.XviD.[www.DivxTotaL.com]", "Lost"),
    ("4-13 Cursed (HD)", "Cursed"),
    ("Dragon Ball Z Movie - 09 - Bojack Unbound - 1080p BluRay x264 DTS 5.1 -DDR", "Dragon Ball Z Movie - 09 - Bojack Unbound"),
    ("[F-D] Fairy Tail Season 1 - 6 + Extras [480P][Dual-Audio]", "Fairy Tail"),
    ("BoJack Horseman [06x01-08 of 16] (2019-2020) WEB-DLRip 720p", "BoJack Horseman"),
    ("[HR] Boku no Hero Academia 87 (S4-24) [1080p HEVC Multi-Subs] HR-GZ", "Boku no Hero Academia"),
    ("Bleach 10º Temporada - 215 ao 220 - [DB-BR]", "Bleach"),
    ("Naruto Shippuden - 107 - Strange Bedfellows", "Naruto Shippuden"),
    ("[224] Shingeki no Kyojin - S03 - Part 1 - 13 [BDRip.1080p.x265.FLAC]", "Shingeki no Kyojin"),
    ("[Erai-raws] Shingeki no Kyojin Season 3 - 11 [1080p][Multiple Subtitle]", "Shingeki no Kyojin"),
    ("La famille bélier", "La famille bélier"),
    ("Mr. Nobody", "Mr. Nobody"),
    ("doctor_who_2005.8x12.death_in_heaven.720p_hdtv_x264-fov", "doctor who"),
    ("[GM-Team][国漫][太乙仙魔录 灵飞纪 第3季][Magical Legend of Rise to immortality Ⅲ][01-26][AVC][GB][1080P]", "Magical Legend of Rise to immortality Ⅲ"),
    ("【喵萌奶茶屋】★01月新番★[Rebirth][01][720p][简体][招募翻译]", "Rebirth"),
    ("【喵萌奶茶屋】★01月新番★[別對映像研出手！/映像研には手を出すな！/Eizouken ni wa Te wo Dasu na!][01][1080p][繁體]", "Eizouken ni wa Te wo Dasu na!"),
    ("【喵萌奶茶屋】★01月新番★[別對映像研出手！/Eizouken ni wa Te wo Dasu na!/映像研には手を出すな！][01][1080p][繁體]", "Eizouken ni wa Te wo Dasu na!"),
    ("[Seed-Raws] 劇場版 ペンギン・ハイウェイ Penguin Highway The Movie (BD 1280x720 AVC AACx4 [5.1+2.0+2.0+2.0]).mp4", "Penguin Highway The Movie"),
    ("[SweetSub][Mutafukaz / MFKZ][Movie][BDRip][1080P][AVC 8bit][简体内嵌]", "Mutafukaz / MFKZ"),
    ("[Erai-raws] Kingdom 3rd Season - 02 [1080p].mkv", "Kingdom"),
    ("Голубая волна / Blue Crush (2002) DVDRip", "Blue Crush"),
    ("Жихарка (2007) DVDRip", "Жихарка"),
    ("3 Миссия невыполнима 3 2006г. BDRip 1080p.mkv", "3 Миссия невыполнима 3"),
    ("1. Детские игры. 1988. 1080p. HEVC. 10bit..mkv", "1. Детские игры."),
    ("01. 100 девчонок и одна в лифте 2000 WEBRip 1080p.mkv", "01. 100 девчонок и одна в лифте"),
    ("08.Планета.обезьян.Революция.2014.BDRip-HEVC.1080p.mkv", "08 Планета обезьян Революция"),
    ("Американские животные / American Animals (Барт Лэйтон / Bart Layton) [2018, Великобритания, США, драма, криминал, BDRip] MVO (СВ Студия)", "American Animals"),
    ("Греческая смоковница / Griechische Feigen / The Fruit Is Ripe (Зиги Ротемунд / Sigi Rothemund (as Siggi Götz)) [1976, Германия (ФРГ), эротика, комедия, приключения, DVDRip] 2 VO", "Griechische Feigen / The Fruit Is Ripe"),
    ("Греческая смоковница / The fruit is ripe / Griechische Feigen (Siggi Götz) [1976, Германия, Эротическая комедия, DVDRip]", "The fruit is ripe / Griechische Feigen"),
    ("Бастер / Buster (Дэвид Грин / David Green) [1988, Великобритания, Комедия, мелодрама, драма, приключения, криминал, биография, DVDRip]", "Buster"),
    ("(2000) Le follie dell'imperatore - The Emperor's New Groove (DvdRip Ita Eng AC3 5.1).avi", "Le follie dell'imperatore - The Emperor's New Groove"),
    ("[NC-Raws] 间谍过家家 / SPY×FAMILY - 04 (B-Global 1920x1080 HEVC AAC MKV)", "SPY×FAMILY"),
    ("GTO (Great Teacher Onizuka) (Ep. 1-43) Sub 480p lakshay", "GTO (Great Teacher Onizuka)"),
    ("Книгоноши / Кнiганошы (1987) TVRip от AND03AND | BLR", "Кнiганошы"),
    ("Yurusarezaru_mono2.srt", "Yurusarezaru mono2"),
])
def test_title_extraction(test_string, expected_title):
    data = parse(test_string, remove_trash=False)
    assert data.parsed_title == expected_title, f"Failed for '{test_string}' with expected '{expected_title}'"