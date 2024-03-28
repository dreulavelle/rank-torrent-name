import pyperf

from RTN import RTN, DefaultRanking, SettingsModel, batch_parse, parse

# Setup
settings = SettingsModel()
ranking_model = DefaultRanking()
rtn = RTN(settings=settings, ranking_model=ranking_model)


titles_infohashes = [
    (f"Movie.Title.{i}.1080p.BluRay.x264", "30bfd9a796679bbeb0e110c17f32148ab8fd5746")
    for i in range(1, 1001)
]
titles = [title for title, _ in titles_infohashes]

# Benchmark Functions
def single_parse_benchmark():
    parse(titles[0])

def batch_parse_small_benchmark():
    batch_parse(titles[:10], chunk_size=10)

def batch_parse_large_benchmark():
    batch_parse(titles, chunk_size=500)

def single_rank_benchmark():
    rtn.rank(*titles_infohashes[0])

def batch_rank_small_benchmark():
    rtn.batch_rank(titles_infohashes[:10], max_workers=4) # type: ignore

def batch_rank_large_benchmark():
    rtn.batch_rank(titles_infohashes, max_workers=8) # type: ignore


runner = pyperf.Runner(loops=1)

runner.bench_func("Parsing Benchmark (1x item)", single_parse_benchmark)
runner.bench_func("Batch Parse Benchmark - Small - (10x items)", batch_parse_small_benchmark)
runner.bench_func("Batch Parse Benchmark - Large - (1000 items)", batch_parse_large_benchmark)
runner.bench_func("Ranking Benchmark (1x item)", single_rank_benchmark)
runner.bench_func("Batch Rank Benchmark - Small - (10x items)", batch_rank_small_benchmark)
runner.bench_func("Batch Rank Benchmark - Large -  (1000 items)", batch_rank_large_benchmark)
