# TORRENTIO_URL = "https://torrentio.strem.fun"
# TORRENTIO_FILTERS = "qualityfilter=other,scr,cam"

# def scrape_show(imdbid: str = "tt0944947", season: int = 1, episode: int = 1) -> dict:
#     """Scrape a show from torrentio"""
#     url = f"{TORRENTIO_URL}/{TORRENTIO_FILTERS}/stream/series/{imdbid}:{season}:{episode}.json"
#     response = requests.get(url)
#     return response.json()

# def scrape_movie(imdbid: str = "tt0172495") -> dict:
#     """Scrape a movie from torrentio"""
#     url = f"{TORRENTIO_URL}/{TORRENTIO_FILTERS}/stream/movie/{imdbid}.json"
#     response = requests.get(url)
#     return response.json()

# def test_scrape_results_with_rank(settings_model, default_ranking) -> dict:
#     """Scrape a show from torrentio"""
#     results = {}
    
#     response: list = scrape_show().get("streams", [])
#     for result in response:
#         results[result["title"].split("\n")[0]] = result["infoHash"]
    
#     for k, v in results.items():
#         print(k, v)

# Sample data for testing
# data = [
#     {"title": "Game of Thrones (2011) Complete [2160p] [HDR] [5.1 5.1] [ger eng] [Vio]", "infohash": "e15ed82226e34aec738cfa691aeb85054df039de"},
#     {"title": "Game.of.Thrones.S01.2160p.UHD.BluRay.x265.10bit.HDR.TrueHD.7.1.Atmos-DON[rartv]", "infohash": "98fa5648554a67748bed7f8cf58559b2660a5c4d"},
#     {"title": "Game of Thrones Season 1 (S01) 2160p HDR 5.1 x265 10bit Phun Psyz", "infohash": "30eaa43096f11a553ce182f97963e5384a4ac781"},
#     {"title": "Game.of.Thrones.S01.2160p.DoVi.HDR.BluRay.REMUX.HEVC.DTS-HD.MA.TrueHD.7.1.Atmos-PB69", "infohash": "f33ce65b218f7c51d65a69d90b09e46c2381c8ef"},
#     {"title": "Game.of.Thrones.S01.2160p.BluRay.REMUX.HEVC.DTS-HD.MA.TrueHD.7.1.Atmos-FGT", "infohash": "605b8f1c0032682c4826caf68db37b361199b2de"},
#     {"title": "Game.of.Thrones.S01.2160p.UHD.BluRay.x265-SCOTLUHD", "infohash": "1873026cfdb096563d5a7871af5de8230895bc1b"},
#     {"title": "Game Of Thrones (2011) Season 01 S01 REPACK (2160p BluRay X265 HEVC 10bit AAC 7.1 Joy) [UTR]", "infohash": "18be909ecb8eb713bd3386289e957469472affc4"},
#     {"title": "Game.Of.Thrones.S01-S04.BluRay.4K.UHD.H265", "infohash": "a6cf5d8fb38570ad91b2bc42e132d244a94bbfde"},
#     {"title": "Game of Thrones S01E01 2160p UHD BluRay x265-SCOTLUHD [eztv]", "infohash": "e4aae367b822794d37d8cafd5a628db985d65fb4"},
#     {"title": "Game of Thrones S01-S05 1080p 10bit BluRay 6CH x265 HEVC", "infohash": "995d57e19453c6cf0559ef36f79540677b2e9c92"},
#     {"title": "Game.Of.Thrones.S01-S06.1080p.Bluray.x265.10bit.AAC.7.1.DUAL.Tigole", "infohash": "98a9d06dc22f870d8ce631fd87ec8781da74ec89"},
#     {"title": "Game.of.Thrones.S01-07.BDRip.1080p", "infohash": "a77ee5dde49e75f171da79ef2fcfafc18be493fa"},
#     {"title": "Game of Thrones - Temporadas Completas (1080p) Acesse o ORIGINAL WWW.BLUDV.TV", "infohash": "4620cc06dcc4076398b76e5d37ada6c5a4943d9b"},
#     {"title": "Game Of Thrones - Season 1 to 6 (Eng Subs) - Mp4 1080p", "infohash": "099a12cc77fb1198323a21d3a340cca79ffd9fc0"},
#     {"title": "Game Of Thrones Season 1 S01 Complete (1080p Bluray X265 HEVC AAC 5.1 Joy) [UTR]", "infohash": "cab9c152593671f3c08bfb31098cef2dfc49caf7"},
#     {"title": "Game.of.Thrones.Season.1-8.S01-08.COMPLETE.1080p.BluRay.WEB.x265.10bit.6CH.ReEnc-LUMI", "infohash": "fba84caa1391fbd75698b131fb57321313e5f3c8"},
#     {"title": "Game of Thrones (2011) 1080p MKV S01E01 Eng NL Subs DMT", "infohash": "a3a89f4a8955cd2b4e8d7f2164604e4e99cfc585"},
#     {"title": "Game Of Thrones - The Complete Collection (2011-2019) BDRip 1080p", "infohash": "cb7ef5f4316a2399dc52d99c63666567df6b0cae"},
#     {"title": "Game.of.Thrones.SEASON.01.S01.COMPLETE.1080p.10bit.BluRay.6CH.x265.HEVC-PSA", "infohash": "31a5ea99284b3603e94ef861311b6bb29345c6d2"},
#     {"title": "Game.of.Thrones.S01-S08.COMPLETE.SERIES.REPACK.1080p.Bluray.x265-HiQVE", "infohash": "31dc5a9e2d92b34ef86e12e626df17368f898571"},
#     {"title": "Game.of.Thrones.S01.1080p.BluRay.REMUX.AVC.TrueHD.7.1.Atmos-BiZKiT[rartv]", "infohash": "0815928549592de3dd02b864bb12a5c3fda8c21c"},
#     {"title": "Juego de tronos Temporada 1 completa [BDremux 1080p][DTS 5.1 Castellano-DTS 5.1 Ingles+Subs][ES-EN]", "infohash": "b76d894ff0555c8fdf22c0a071876d0a2fef8dab"},
#     {"title": "Game of Thrones (Integrale) MULTi HDLight 1080p HDTV", "infohash": "12798d47905228869b9e36c42b382135ac938502"},
#     {"title": "Juego de tronos Temporada 1 [BDremux 1080p][DTS 5.1 Castellano-DTS 5.1 Ingles+Subs][ES-EN]", "infohash": "6be442cb637ee669c3e87d4b15e26613bd5643d4"},
#     {"title": "Game of Thrones - The Iron Anniversary (2021) Season 1 S01 + Extras (1080p HMAX WEB-DL x265 HEVC 10bit AC3 2.0 t3nzin) [QxR]", "infohash": "91a0e224b67de4242b4098236fd29f79f7fbeee3"},
#     {"title": "Game of Thrones Season 1 to 8 The Complete Collection [NVEnc H265 1080p][AAC 6Ch][English Subs]", "infohash": "2b01c3f588cef67d999dc2aefef87678cb011213"},
#     {"title": "Il.Trono.Di.Spade.S01E01-10.BDMux.1080p.AC3.ITA.ENG.SUBS.HEVC", "infohash": "99294a0d3d14ddac6341f788245f783d983c577a"},
#     {"title": "Game.of.Thrones.S01.1080p.BluRay.10bit.HEVC-MkvCage Season 1 One", "infohash": "ae6e5204fea10ed9fa385246317b9ed42fd7362c"},
#     {"title": "Game of Thrones S01 1080p BluRay-RMZ x264-Belex Dual Audio DTS +", "infohash": "90c07facb1f4c1bd9e550780e266b763e7cadaf9"},
#     {"title": "Игра престолов / Game of Thrones [S01-08] (2013-2022) BDRip 1080p от Generalfilm | D | P", "infohash": "60a9eaeeacdba5198b803c9ec16f71f0acd79108"},
#     {"title": "Game of Thrones s01e01 2011 1080p Rifftrax 6ch x265 HEVC", "infohash": "ebaba1042262fb8aef1f7df52175a913ec8b5233"},
#     {"title": "Game of Thrones S01 1080p BluRay H264 AC3 Will1869", "infohash": "c3445760929fc4b682a0de3757d5ffe7c4f76e3a"},
#     {"title": "Game.of.Thrones.S01.ITA.ENG.AC3.1080p.H265-BlackEgg", "infohash": "9634006039f7f70b02acef9dd47e5162dc07f1c1"},
#     {"title": "Game.of.Thrones.S01.1080p.BluRay.x264-HD4U Season 1 One Complete", "infohash": "bdbf9ef10abc728fdce28fc57ae64895551ab3e3"},
#     {"title": "Game of Thrones Seasons 1 to 8 The Complete Box Set/Series [English Subs][NVEnc H265 720p][AAC 6Ch]", "infohash": "b75cdb066d9de77c4ede1eed595b26a784ccffb6"},
#     {"title": "Game of Thrones 1ª a 7ª Temporada Completa [720p] [BluRay] [DUAL", "infohash": "b39b4e0485fa2a5da0eec4465f54963cf586d39d"},
#     {"title": "Game of Thrones - Season 1 - 720p BluRay - x264 - ShAaNiG", "infohash": "736b3dc769e32d91cfd3b6b70fac7f1bfe0ed7c7"},
#     {"title": "Game.Of.Thrones.Season.1-4.Complete.720p.x264.Arabic-sub", "infohash": "5ec7d86e60054befdebf5774a290a972b12d2ed3"},
#     {"title": "Game of Thrones S01-S07 720p BRRip 33GB - MkvCage", "infohash": "87d273b810ffecee121fb7e10390ac7ef21b5b18"},
#     {"title": "Game of Thrones 1ª a 8ª Temporada Completa [720p-1080p] [BluRay] [DUAL]", "infohash": "00f32a20b6afa030a403a8659621bdb05cba5cfd"},
#     {"title": "Game of Thrones S01E01 720p HDTV x264-CTU [eztv]", "infohash": "0b29678265e6f6e20ece91f50a502462adcb835f"},
#     {"title": "Game of Thrones - Temporadas Completas (720p) Acesse o ORIGINAL WWW.BLUDV.TV", "infohash": "d653731eef4ad4b01fb28d113296ef10c0c30ad9"},
#     {"title": "Game of Thrones Season 1 S01 720p BluRay x264", "infohash": "04bba4e2f593241ac407ca83b2b44f3849039f76"},
#     {"title": "Game.of.Thrones.Complete.Series.Season.1.2.3.4.5.6.7.8.x264.720p", "infohash": "36b0bb34fa1dc6a892b7b40707ff8f6f2b5d30b7"},
#     {"title": "Game of Thrones S01 Complete 720p BluRay x264 Hindi English[MW]", "infohash": "046603a1833bb3d28e615b46406e29220b5bf6a5"},
#     {"title": "Juego De Tronos Temporada-1 Completa 720p Español De Esp", "infohash": "40a380ce1ab6741cc7d50a0fb435063a5d7562c8"},
#     {"title": "Игра престолов / Game of Thrones [S01-08] (2011-2019) BDRip 720p | LostFilm", "infohash": "3e3e5b7d59187dc2150c4d968052e1b329728375"},
#     {"title": "Game.of.Thrones.S01.COMPLETE.720p.10bit.BluRay.2CH.x265.HEVC-PSA", "infohash": "916059a3ea6e0b4b5f515e2c608060b38aeea09d"},
#     {"title": "Game of Thrones Season Pack S01 to S08 480p English x264", "infohash": "b8cb8da176efca9706f33fe599801d76ba237a99"},
#     {"title": "Game of Thrones Seasons 1-5 CENSORED", "infohash": "eeaee628e7cd199b9b5c64f668a99a02dc493824"},
#     {"title": "game of thrones 1-4 temporada sub-español", "infohash": "38211f64a97f3ec2711b5a8490fa2b34f7b66633"},
#     {"title": "Game of Thrones Temporada 1 Español Latino", "infohash": "10af31f4a9edc56539b55595f90c7544f0b05f7b"}
# ]