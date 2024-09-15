# Ranking Torrents

2. **Rank a Torrent:** Feed a torrent title to RTN to parse it and calculate its rank based on your settings.

```python
from RTN import RTN
from RTN.models import DefaultRanking

rtn = RTN(settings=settings, ranking_model=DefaultRanking())
torrent = rtn.rank("Example.Movie.2020.1080p.BluRay.x264-Example", "infohash123456")
```

3. **Inspecting the Torrent Object:** The returned `Torrent` object includes parsed data and a rank. Access its properties to understand its quality:

```python
print(f"Title: {torrent.data.parsed_title}, Rank: {torrent.rank}")
```

### Sorting Torrents

4. **Sort Multiple Torrents:** If you have multiple torrents, RTN can sort them based on rank, helping you select the best one.

```python
torrents = [rtn.rank(title, "infohash") for title in torrent_titles]
sorted_torrents = RTN.sort(torrents)
```

## Torrent Object

A `Torrent` object encapsulates metadata about a torrent, such as its title, parsed information, and rank. Here's an example structure:

```python
Torrent(
    raw_title="Example.Movie.2020.1080p.BluRay.x264-Example",
    infohash="infohash123456",
    data=ParsedData(parsed_title='Example Movie', ...),
    fetch=True,
    rank=150,
    lev_ratio=0.95
)
```

## Understanding **SettingsModel** and **RankingModel**

**SettingsModel** and **RankingModel** play crucial roles in RTN, offering users flexibility in filtering and ranking torrents according to specific needs. Here's what each model offers and why they are important:

### SettingsModel

`SettingsModel` is where you define your filtering criteria, including patterns to require, exclude, and prefer in torrent names. This model allows for dynamic configuration of torrent selection based on user-defined patterns and preferences. 

Key functionalities:
- **Filtering Torrents:** Determine which torrents to consider or ignore based on matching patterns.
- **Prioritizing Torrents:** Indicate preferred attributes that give certain torrents higher precedence.
- **Custom Ranks Usage:** Decide how specific attributes influence the overall ranking, enabling or disabling custom ranks.

Example usage:
```python
from RTN.models import SettingsModel, CustomRank

settings = SettingsModel(
    require=["1080p", "4K"],
    exclude=["CAM"],
    preferred=["HDR", "/SenSiTivE/"],
    ...
)
```

As shown above with **"/SenSiTivE/"**, you are able to set explicit case sensitivity as well for entering patterns for `require`, `exclude` and `preferred` attributes. We default to ignore case sensitivity.

### RankingModel

While `SettingsModel` focuses on the selection and preference of torrents, `RankingModel` (such as `BaseRankingModel` or its extensions) is designed to compute the ranking scores based on those preferences. This model allows for the creation of a nuanced scoring system that evaluates each torrent's quality and attributes, translating user preferences into a quantifiable score.

Key functionalities:
- **Scoring Torrent Attributes:** Assign scores to various torrent attributes like resolution, audio quality, etc.
- **Customizable Ranking Logic:** Extend `BaseRankingModel` to tailor ranking criteria and values, enhancing the decision-making process in selecting torrents.

### Why Both Models are Necessary

`SettingsModel` and `RankingModel` work together to provide a comprehensive approach to torrent ranking:
- **SettingsModel** specifies what to look for in torrents, defining the search and preference criteria. This is what the user sets and edits.
- **RankingModel** quantifies those preferences, assigning scores to make informed decisions on which torrents are of higher quality and relevance. This is the default ranking model that RTN uses if no custom ranking model is provided from the user.

This separation allows for flexible configuration and a powerful, customizable ranking system tailored to individual user preferences.

### BaseRankingModel

Here is the default BaseRankingModel that RTN uses, and it's attributes.

- [BaseRankingModel](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py#L171)

# Real World Example

Here is a crude example of how you could use RTN in scraping.

```py
from RTN import RTN, Torrent, DefaultRanking
from RTN.exceptions import GarbageTorrent

settings = SettingsModel()
ranking = DefaultRanking()
rtn = RTN(settings=settings, ranking_model=ranking)


# Define some function for scraping for results from some API.
def scrape_results(response: Response, query: str):
    if response.ok:
        torrents = set()
        for stream in response.streams:
            try:
                torrent: Torrent = rtn.rank(stream.title, stream.infohash, remove_trash=True)
            except GarbageTorrent:
                # One thing to note is that as we parse titles, we also get rid of garbage.
                # Feel free to add your own logic when this happens!
                # You can bypass this by setting `remove_trash` to `False` in `rank`.
                pass
            if torrent and torrent.fetch:
                # If torrent.fetch is True, then it's a good torrent,
                # as considered by your ranking profile and settings model.
                torrents.add(torrent)

        # Sort the list of torrents based on their rank in descending order, keeping resolutions in mind.
        sorted_torrents = sort_torrents(torrents)
        return sorted_torrents
    ...

# Example usage
for torrent in sorted_torrents:
    print(f"Title: {torrent.data.parsed_title}, Infohash: {torrent.infohash}, Rank: {torrent.rank}")
```

# ParsedData Structure

Here is all of the attributes of `data` from the `Torrent` object, along with their default values.

This is accessible at `torrent.data` in the `Torrent` object. Ex: `torrent.data.resolution`

- [ParsedData](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py#L32)

# Performance Benchmarks

Here, we dive into the heart of RTN's efficiency, showcasing how it performs under various loads. Whether you're parsing a single title or ranking thousands, understanding these benchmarks will help you optimize your use of RTN.

### Benchmark Categories

We categorize benchmarks into two main processes:
- **Parsing**: Measures the time to parse a title and return a `ParsedData` object.
- **Ranking**: A comprehensive process that includes parsing and then evaluates the title based on defined criteria. This represents a more "real-world" scenario and is crucial for developers looking to integrate RTN effectively.

### Benchmark Results

To facilitate comparison, we've compiled the results into a single table:

| Operation                                    | Items Count | Mean Time    | Standard Deviation |
|----------------------------------------------|-------------|--------------|--------------------|
| **Parsing Benchmark (Single item)**          | 1           | 583 us       | 10 us              |
| **Batch Parse Benchmark (Small batch)**      | 10          | 6.24 ms      | 0.16 ms            |
| **Batch Parse Benchmark (Large batch)**      | 1000        | 1.57 s       | 0.06 s             |
| **Batch Parse Benchmark (XLarge batch)**     | 2000        | 3.62 s       | 0.11 s             |
| **Ranking Benchmark (Single item)**          | 1           | 616 us       | 11 us              |
| **Batch Rank Benchmark (Small batch)**       | 10          | 24.6 ms      | 2.4 ms             |
| **Batch Rank Benchmark (Large batch)**       | 1000        | 3.13 s       | 0.15 s             |
| **Batch Rank Benchmark (XLarge batch)**      | 2000        | 6.27 s       | 0.13 s             |

> :warning: Test Bench consisted of **R9 5900X CPU** and **64GB DDR4 RAM** - Your mileage may vary!

This data shows RTN's robust capability to efficiently process both small and extensive datasets.
To run your own benchmark, you can clone the repo and run `make benchmark` from inside the root of the repository.
