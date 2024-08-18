import pyperf
import os
import sys
from contextlib import contextmanager

from RTN import RTN, DefaultRanking, SettingsModel, parse
from RTN.models import ParsedData, Torrent

settings = SettingsModel()
ranking_model = DefaultRanking()
rtn = RTN(settings=settings, ranking_model=ranking_model)

titles_infohashes = [
    (f"Movie.Title.{i}.1080p.BluRay.x264", "30bfd9a796679bbeb0e110c17f32148ab8fd5746")
    for i in range(1, 2001)
]
titles = [title for title, _ in titles_infohashes]

@contextmanager
def suppress_output():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

# Benchmark Functions
def single_parse_benchmark():
    with suppress_output():
        assert isinstance(parse("Movie.Title.1.1080p.BluRay.x264"), ParsedData)

def parse_small_benchmark():
    with suppress_output():
        for title in titles[:10]:
            assert isinstance(parse(title), ParsedData)

def parse_large_benchmark():
    with suppress_output():
        for title in titles[:1000]:
            assert isinstance(parse(title), ParsedData)

def parse_xlarge_benchmark():
    with suppress_output():
        for title in titles:
            assert isinstance(parse(title), ParsedData)

def single_rank_benchmark():
    with suppress_output():
        rtn.rank("Movie.Title.1.1080p.BluRay.x264", "30bfd9a796679bbeb0e110c17f32148ab8fd5746")

def rank_small_benchmark():
    with suppress_output():
        for title, infohash in titles_infohashes[:10]:
            assert isinstance(rtn.rank(title, infohash), Torrent)

def rank_large_benchmark():
    with suppress_output():
        for title, infohash in titles_infohashes[:1000]:
            assert isinstance(rtn.rank(title, infohash), Torrent)

def rank_xlarge_benchmark():
    with suppress_output():
        for title, infohash in titles_infohashes:
            assert isinstance(rtn.rank(title, infohash), Torrent)


runner = pyperf.Runner()
runner.bench_func("Parsing Benchmark (1x item)", single_parse_benchmark)
runner.bench_func("Batch Parse Benchmark - Small - (10x items)", parse_small_benchmark)
runner.bench_func("Batch Parse Benchmark - Large - (1000 items)", parse_large_benchmark)
runner.bench_func("Batch Parse Benchmark - XLarge - (2000 items)", parse_xlarge_benchmark)
runner.bench_func("Ranking Benchmark (1x item)", single_rank_benchmark)
runner.bench_func("Batch Rank Benchmark - Small - (10x items)", rank_small_benchmark)
runner.bench_func("Batch Rank Benchmark - Large -  (1000 items)", rank_large_benchmark)
runner.bench_func("Batch Rank Benchmark - XLarge - (2000 items)", rank_xlarge_benchmark)