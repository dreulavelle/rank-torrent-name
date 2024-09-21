# Why? 

Here are the key points about how ranking works in Rank Torrent Name (RTN):

1. RTN uses a customizable ranking system that allows users to define their preferences for filtering and ranking torrents.
2. The ranking process involves parsing the torrent name and evaluating it based on defined criteria.
3. Users can modify the `SettingsModel` to specify their preferences, including patterns to look for, attributes to exclude, and preferences for features like resolution and audio quality.
4. The ranking system uses a `RankingModel` to compute scores based on user-defined preferences, allowing for a nuanced scoring system.
5. The process includes parsing the torrent title, extracting metadata, and calculating a rank based on the settings and ranking model.
6. RTN can sort multiple torrents based on their calculated ranks to help users choose the best option.
7. The ranking takes into account various factors like resolution, audio quality, and other user-defined criteria.
8. The system allows for dynamic adjustment of ranking criteria at runtime, giving users flexibility in how torrents are evaluated.
9. RTN uses a Levenshtein ratio in tangent with normalization to ensure accuracy by comparing parsed titles with original titles.

In summary, Rank Torrent Name provides a flexible and customizable system for ranking torrents based on user-defined criteria, allowing for detailed analysis and sorting of torrent metadata to find the best quality options.

---

## Installation

You can install `rank-torrent-name` using pip:

```bash
pip install rank-torrent-name
```

or you can add it to your project through `Poetry` as well,

```bash
poetry add rank-torrent-name
```

---

## 🎉 Quick Start

### Ranking Torrents

2. **Rank a Torrent:** Feed a torrent title to RTN to parse it and calculate its rank based on your settings.

```python
from RTN import RTN
from RTN.models import DefaultRanking, SettingsModel

settings = SettingsModel() # you can modify the settings model to your liking.
rtn = RTN(settings=settings, ranking_model=DefaultRanking())
torrent = rtn.rank("Example.Movie.2020.1080p.BluRay.x264-Example", "1231231231231231231231231231231231231231")

print(torrent.data.parsed_title) # "Example Movie"
print(torrent.rank) # 600
print(torrent.fetch) # True
print(torrent.data.trash) # False
```

1. **Inspecting the Torrent Object:** The returned `Torrent` object includes parsed data and a rank. Access its properties to understand its quality:

```python
print(f"Title: {torrent.data.parsed_title}, Rank: {torrent.rank}")
```

!!! warning Ratio
    To get a ratio you must provide the `correct_title` parameter in `.rank()`. This is what's used to calculate the ratio. This needs to be the metadata title, not the raw title.
    If you don't have the metadata title, you can provide the query from the user instead.
---

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

---

## Understanding SettingsModel and RankingModel

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
    custom_ranks={
        "uhd": CustomRank(enable=True, fetch=True, rank=200),
        "hdr": CustomRank(enable=True, fetch=True, rank=100),
    }
)
```

As shown above with **"/SenSiTivE/"**, you are able to set explicit case sensitivity as well for entering patterns for `require`, `exclude` and `preferred` attributes. We default to ignore case sensitivity.

### RankingModel

While `SettingsModel` focuses on the selection and preference of torrents, `RankingModel` (such as `BaseRankingModel` or its extensions) is designed to compute the ranking scores based on those preferences. This model allows for the creation of a nuanced scoring system that evaluates each torrent's quality and attributes, translating user preferences into a quantifiable score.

Key functionalities:
- **Scoring Torrent Attributes:** Assign scores to various torrent attributes like resolution, audio quality, etc.
- **Customizable Ranking Logic:** Extend `BaseRankingModel` to tailor ranking criteria and values, enhancing the decision-making process in selecting torrents.

Example usage:
```python
from RTN.models import BaseRankingModel

class MyRankingModel(BaseRankingModel):
    uhd = 200  # Ultra HD content
    hdr = 100  # HDR content
    # Define more attributes and scores as needed
```

### Why Both Models are Necessary

`SettingsModel` and `RankingModel` work together to provide a comprehensive approach to torrent ranking:
- **SettingsModel** specifies what to look for in torrents, defining the search and preference criteria.
- **RankingModel** quantifies those preferences, assigning scores to make informed decisions on which torrents are of higher quality and relevance.

This separation allows for flexible configuration and a powerful, customizable ranking system tailored to individual user preferences.

Create as many `SettingsModel` and `RankingModel` as you like to use anywhere in your code. They are mean't to be used as a way to version settings for your users. 

---

# Real World Example

Here is a crude example of how you could use RTN in scraping.

```py
from RTN import RTN, Torrent, DefaultRanking
from RTN.exceptions import GarbageTorrent

# Assuming 'settings' is defined somewhere and passed correctly.
rtn = RTN(settings=settings, ranking_model=DefaultRanking())
...
# Define some function for scraping for results from some API.
    if response.ok:
        torrents = set()
        for stream in response.streams:
            try:
                torrent: Torrent = rtn.rank(
                    stream.title,
                    infohash=stream.infohash
                    correct_title=correct_title_or_query,
                    remove_trash=True
                )
            except GarbageTorrent:
                # One thing to note is that as we parse titles, we also get rid of garbage.
                # Feel free to add your own logic when this happens!
                # You can bypass this by setting `remove_trash` to `False` in the `rank` method.
                continue
            if torrent and torrent.fetch:
                # If torrent.fetch is True, then it's a good torrent,
                # as considered by your ranking profile and settings model.
                torrents.add(torrent)

        # Sort the list of torrents based on their rank in descending order, and resolution buckets intact.
        return sort_torrents(torrents)
    ...

# Example usage
for torrent in sorted_torrents:
    print(f"Title: {torrent.data.parsed_title}, Infohash: {torrent.infohash}, Rank: {torrent.rank}")
```

---

# ParsedData Structure

Here is all of the attributes of `data` from the `Torrent` object, along with their default values.

This is accessible at `torrent.data` in the `Torrent` object. 
Example: 

```python
print(torrent.data.resolution) # '1080p'
```

!!! tip "Missing something?"
    Don't see something you want in the list? Submit a [Feature Request](https://github.com/dreulavelle/rank-torrent-name/issues/new?assignees=dreulavelle&labels=kind%2Ffeature%2Cstatus%2Ftriage&projects=&template=---feature-request.yml) to have it added!

## Performance Benchmarks

Here, we dive into the heart of RTN's efficiency, showcasing how it performs under various loads. Whether you're parsing a single title or ranking thousands, understanding these benchmarks will help you optimize your use of RTN.

### Benchmark Categories

We categorize benchmarks into two main processes:

- **Parsing**: Measures the time to parse a title and return a `ParsedData` object. This process focuses solely on extracting information from the torrent title.
- **Ranking**: A comprehensive process that includes parsing and then evaluates the title based on defined criteria. It outputs a `Torrent` model, which includes a `data` attribute containing the `ParsedData` and additional ranking information. This represents a more "real-world" scenario and is crucial for developers looking to integrate RTN effectively.

### Benchmark Results

To facilitate comparison, we've compiled the results into a single table:

!!! warning "Benchmarks Comparisons"

    | Operation                                    | Items Count | Mean Time    | Standard Deviation |
    |----------------------------------------------|-------------|--------------|--------------------|
    | **Parsing Benchmark (Single item)**          | 1           | 779 us       | 36 us              |
    | **Batch Parse Benchmark (Small batch)**      | 10          | 7.67 ms      | 0.38 ms            |
    | **Batch Parse Benchmark (Large batch)**      | 1000        | 776 ms       | 24 ms              |
    | **Batch Parse Benchmark (XLarge batch)**     | 2000        | 1.55 s       | 0.04 s             |
    | **Ranking Benchmark (Single item)**          | 1           | 796 us       | 15 us              |
    | **Batch Rank Benchmark (Small batch)**       | 10          | 7.98 ms      | 0.19 ms            |
    | **Batch Rank Benchmark (Large batch)**       | 1000        | 806 ms       | 11 ms              |
    | **Batch Rank Benchmark (XLarge batch)**      | 2000        | 1.65 s       | 0.05 s             |

!!! note "Test Bench Specs"
    Test Bench consisted of **R9 5900X CPU** and **64GB DDR4 RAM** - Your mileage may vary.

This data shows RTN's robust capability to efficiently process both small and extensive datasets.

* To run your own benchmark, you can clone the repo and run `make benchmark` from inside the root of the repository.