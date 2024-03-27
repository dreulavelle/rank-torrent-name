import pyperf

from RTN import RTN, DefaultRanking, SettingsModel, parse

settings = SettingsModel()
ranking_model = DefaultRanking()
rtn = RTN(settings=settings, ranking_model=ranking_model)

def single_parse_benchmark_run():
    parse("The.Mandalorian.S01E02.1080p.DSNP.WEB-DL.x264")

def multi_parse_benchmark_run():
    titles = [
        "The.Matrix.1999.1080p.BluRay.x264",
        "Inception.2010.720p.BRRip.x264",
        "Avengers.Endgame.2019.2160p.UHD.BluRay.x265",
        "Interstellar.2014.IMAX.BDRip.x264",
        "Game.of.Thrones.S01E01.1080p.WEB-DL.x264",
        "Breaking.Bad.S05E14.720p.HDTV.x264",
        "The.Witcher.S02E05.2160p.NF.WEBRip.x265",
        "The.Mandalorian.S01E02.1080p.DSNP.WEB-DL.x264",
        "1917.2019.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1",
        "Joker.2019.720p.BluRay.x264"
    ]
    for title in titles:
        parse(title)

def single_benchmark_run():
    rtn.rank("The.Matrix.1999.1080p.BluRay.x264", "30bfd9a796679bbeb0e110c17f32148ab8fd5746")

def multi_benchmark_run():
    titles_infohashes = [
        ("The.Matrix.1999.1080p.BluRay.x264", "30bfd9a796679bbeb0e110c17f32148ab8fd5746"),
        ("Inception.2010.720p.BRRip.x264", "c9b4c5e5789c91823c2117b3550663c6bdd9b965"),
        ("Avengers.Endgame.2019.2160p.UHD.BluRay.x265", "1ba1a10a4409727e85cdba10591a58558a615f13"),
        ("Interstellar.2014.IMAX.BDRip.x264", "7c2c1525a61c6b1377ecbf3c1a3995285ebcd8f7"),
        ("Game.of.Thrones.S01E01.1080p.WEB-DL.x264", "1205555d9771e3a32a065d96dd582d09495661dc"),
        ("Breaking.Bad.S05E14.720p.HDTV.x264", "659cb95e90a52b0ad1bdeaed764716a715ad7599"),
        ("The.Witcher.S02E05.2160p.NF.WEBRip.x265", "c379a0247a6068ce5fb2092cfd7851ac08d8487c"),
        ("The.Mandalorian.S01E02.1080p.DSNP.WEB-DL.x264", "59a34ce306ec1332bf216b531bbc6a014e23e415"),
        ("1917.2019.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1", "1e510d4b0f82eaf552bf7b24e4bba6bd3693341e"),
        ("Joker.2019.720p.BluRay.x264", "fde14883bc2de07ae883bf1449eabc7c4e1a9b84")
    ]
    for title, infohash in titles_infohashes:
        rtn.rank(title, infohash)

runner = pyperf.Runner()
runner.bench_func("Parsing Benchmark (1x)", single_parse_benchmark_run)
runner.bench_func("Parsing Benchmark (10x)", multi_parse_benchmark_run)
runner.bench_func("Ranking Benchmark (1x)", single_benchmark_run)
runner.bench_func("Ranking Benchmark (10x)", multi_benchmark_run)
