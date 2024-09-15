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
from RTN.models import DefaultRanking

# Using the settings model you created above,
rtn = RTN(settings=settings, ranking_model=DefaultRanking())
torrent = rtn.rank("Example.Movie.2020.1080p.BluRay.x264-Example", "infohash123456")
```

3. **Inspecting the Torrent Object:** The returned `Torrent` object includes parsed data and a rank. Access its properties to understand its quality:

```python
print(f"Title: {torrent.data.parsed_title}, Rank: {torrent.rank}")
```

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

### BaseRankingModel

Here is the default BaseRankingModel that RTN uses, and it's attributes.

```py
class BaseRankingModel(BaseModel):
    """
    A base class for ranking models used in the context of media quality and attributes.
    The ranking values are used to determine the quality of a media item based on its attributes.

    Attributes:
        uhd (int): The ranking value for Ultra HD (4K) resolution.
        fhd (int): The ranking value for Full HD (1080p) resolution.
        hd (int): The ranking value for HD (720p) resolution.
        sd (int): The ranking value for SD (480p) resolution.
        bluray (int): The ranking value for Blu-ray quality.
        hdr (int): The ranking value for HDR quality.
        hdr10 (int): The ranking value for HDR10 quality.
        dolby_video (int): The ranking value for Dolby video quality.
        dts_x (int): The ranking value for DTS:X audio quality.
        dts_hd (int): The ranking value for DTS-HD audio quality.
        dts_hd_ma (int): The ranking value for DTS-HD Master Audio audio quality.
        atmos (int): The ranking value for Dolby Atmos audio quality.
        truehd (int): The ranking value for Dolby TrueHD audio quality.
        ddplus (int): The ranking value for Dolby Digital Plus audio quality.
        ac3 (int): The ranking value for AC3 audio quality.
        aac (int): The ranking value for AAC audio quality.
        remux (int): The ranking value for remux attribute.
        webdl (int): The ranking value for web-dl attribute.
        repack (int): The ranking value for repack attribute.
        proper (int): The ranking value for proper attribute.
        dubbed (int): The ranking value for dubbed attribute.
        subbed (int): The ranking value for subbed attribute.
        av1 (int): The ranking value for AV1 attribute.
    """
    # resolution
    uhd: int = 0
    fhd: int = 0
    hd: int = 0
    sd: int = 0
    # quality
    bluray: int = 0
    hdr: int = 0
    hdr10: int = 0
    dolby_video: int = 0
    # audio
    dts_x: int = 0
    dts_hd: int = 0
    dts_hd_ma: int = 0
    atmos: int = 0
    truehd: int = 0
    ddplus: int = 0
    ac3: int = 0
    aac: int = 0
    # other
    remux: int = 0
    webdl: int = 0
    repack: int = 5
    proper: int = 4
    # extras
    dubbed: int = 4
    subbed: int = 2
    av1: int = 0
```

Keep in mind that these are explicitly set within RTN and are needed in order for RTN to work. You can add new attributes, but it will be up to you to handle them.

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
            if not stream.infohash or not title_match(correct_title, stream.title):
                # Skip results that don't match the query.
                # We want to do this first to weed out torrents
                # that are below the 90% match criteria. (Default is 90%)
                continue
            try:
                torrent: Torrent = rtn.rank(stream.title, stream.infohash)
            except GarbageTorrent:
                # One thing to note is that as we parse titles, we also get rid of garbage.
                # Feel free to add your own logic when this happens!
                # You can bypass this by setting `remove_trash` to `False` in `rank` or `parse`.
                pass
            if torrent and torrent.fetch:
                # If torrent.fetch is True, then it's a good torrent,
                # as considered by your ranking profile and settings model.
                torrents.add(torrent)

        # Sort the list of torrents based on their rank in descending order
        sorted_torrents = sorted(list(torrents), key=lambda x: x.rank, reverse=True)
        return sorted_torrents
    ...

# Example usage
for torrent in sorted_torrents:
    print(f"Title: {torrent.data.parsed_title}, Infohash: {torrent.infohash}, Rank: {torrent.rank}")
```

---

# ParsedData Structure

Here is all of the attributes of `data` from the `Torrent` object, along with their default values.

This is accessible at `torrent.data` in the `Torrent` object. Ex: `torrent.data.resolution`

```py
class ParsedData(BaseModel):
    """Parsed data model for a torrent title."""

    raw_title: str
    parsed_title: str
    fetch: bool = False
    is_4k: bool = False
    is_multi_audio: bool = False
    is_multi_subtitle: bool = False
    is_complete: bool = False
    year: int = 0
    resolution: List[str] = []
    quality: List[str] = []
    season: List[int] = []
    episode: List[int] = []
    codec: List[str] = []
    audio: List[str] = []
    subtitles: List[str] = []
    language: List[str] = []
    bitDepth: List[int] = []
    hdr: str = ""
    proper: bool = False
    repack: bool = False
    remux: bool = False
    upscaled: bool = False
    remastered: bool = False
    directorsCut: bool = False
    extended: bool = False
```

This will continue to grow though as we expand on functionality, so keep checking back for this list!

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

!!! note "Test Bench Specs"
    Test Bench consisted of **R9 5900X CPU** and **64GB DDR4 RAM** - Your mileage may vary.

This data shows RTN's robust capability to efficiently process both small and extensive datasets.
To run your own benchmark, you can clone the repo and run `make benchmark` from inside the root of the repository.

