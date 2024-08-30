import pyperf

from RTN import RTN, DefaultRanking, SettingsModel, parse
from RTN.models import ParsedData, Torrent

settings = SettingsModel()
ranking_model = DefaultRanking()
rtn = RTN(settings=settings, ranking_model=ranking_model)

titles_infohashes = [
    (f"Game.of.Thrones.S01.2160p.UHD.BluRay.x265.10bit.HDR.{i}.TrueHD.7.1.Atmos-DON[rartv]", "30bfd9a796679bbeb0e110c17f32148ab8fd5746")
    for i in range(1, 100001)
]
titles = [title for title, _ in titles_infohashes]

def benchmark_parse(n):
    for title in titles[:n]:
        assert isinstance(parse(title), ParsedData)

def benchmark_rank(n):
    for title, infohash in titles_infohashes[:n]:
        assert isinstance(rtn.rank(title, infohash), Torrent)

runner = pyperf.Runner()
runner.bench_func("Parse Benchmark (1x item)", lambda: benchmark_parse(1))
runner.bench_func("Parse Benchmark - Small - (10x items)", lambda: benchmark_parse(10))
runner.bench_func("Parse Benchmark - Large - (1000 items)", lambda: benchmark_parse(1000))
runner.bench_func("Parse Benchmark - XLarge - (2000 items)", lambda: benchmark_parse(2000))
runner.bench_func("Rank Benchmark (1x item)", lambda: benchmark_rank(1))
runner.bench_func("Rank Benchmark - Small - (10x items)", lambda: benchmark_rank(10))
runner.bench_func("Rank Benchmark - Large - (1000 items)", lambda: benchmark_rank(1000))
runner.bench_func("Rank Benchmark - XLarge - (2000 items)", lambda: benchmark_rank(2000))