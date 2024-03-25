# Rank Torrent Name (RTN)

The **Rank Torrent Name** package provides a comprehensive solution for parsing and ranking torrent metadata based on user-defined settings and preferences. With RTN, you can extract detailed information from torrent titles, such as quality, resolution, audio details, and more, and rank them according to customizable criteria.

## Features

- **Torrent Parsing:** Extract and parse metadata from torrent titles using PTN and enrich it with additional information.
- **Customizable Ranking:** Define your own ranking model to prioritize torrents based on various attributes like resolution, audio quality, etc.
- **Flexible Settings:** Configure your preferences for which torrents to fetch, ignore, or give higher precedence.
- **Levenshtein Ratio Comparison:** Utilize similarity scores to compare parsed titles with raw titles for improved accuracy.
- **Easy Integration:** Designed as a package for easy inclusion in your Python projects or applications.

## Installation

Install the RTN package using pip:

```bash
pip install rank-torrent-name
```

Ensure you have Python 3.6 or higher to use RTN.

## Getting Started

Here's a quick guide on how to use RTN in your Python projects.

### 1. Importing the Package

Start by importing RTN and other necessary components from the package:

```python
from RTN import RTN, SettingsModel, DefaultRanking
```

### 2. Setting Up

Define your settings and ranking model. You can start with the default settings and modify them according to your needs.

```python
settings = SettingsModel(
    profile="default",
    require=[],
    exclude=[],
    preferred=["\bS\d+", "Series|Complete|HDR+?"],
    custom_ranks={
        "uhd": {"enable": True, "fetch": True, "rank": -200},
        "fhd": {"enable": True, "fetch": True, "rank": 90},
        "hd": {"enable": True, "fetch": True, "rank": 60},
        "sd": {"enable": True, "fetch": True, "rank": -120},
        "dolby_video": {"enable": True, "fetch": True, "rank": -1000},
        "hdr": {"enable": True, "fetch": True, "rank": -1000},
        "hdr10": {"enable": True, "fetch": True, "rank": -1000},
        "aac": {"enable": True, "fetch": True, "rank": 70},
        "ac3": {"enable": True, "fetch": True, "rank": 50},
        "remux": {"enable": False, "fetch": True, "rank": -75},
        "webdl": {"enable": True, "fetch": True, "rank": 90},
        "bluray": {"enable": True, "fetch": True, "rank": -90},
    },
)

ranking_model = DefaultRanking()
```

### 3. Initializing RTN

Create an instance of RTN with your settings and ranking model.

```python
rtn_instance = RTN(settings=settings, ranking_model=ranking_model)
```

### 4. Parsing and Ranking a Torrent

Use the `rank` method to parse and rank a given torrent title. Replace `"Your.Torrent.Title.Here"` and `"infohash"` with the actual torrent title and infohash.

```python
torrent = rtn_instance.rank("Your.Torrent.Title.Here", "infohash")
```

### 5. Working with the Torrent Object

The returned `Torrent` object contains parsed data, a fetch flag, and a rank. You can access its attributes directly:

```python
print(f"Title: {torrent.raw_title}")
print(f"Rank: {torrent.rank}")
print(f"Fetch: {'Yes' if torrent.fetch else 'No'}")
```

### 6. Sorting Torrents

If you have a list of `Torrent` objects, you can sort them by their rank using the `sort` function:

```python
sorted_torrents = RTN.sort([torrent1, torrent2, torrent3])
```

## Contribution

Contributions are welcome! If you'd like to improve or suggest features for the RTN package, please open an issue or pull request on our GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it as you see fit.

## Acknowledgments

Thanks to all contributors and users of the RTN package. Your feedback and contributions make this project better every day.

---

Remember to replace placeholders (like the package name in the installation command) with actual values relevant to your project. This README provides a starting point, but consider adding more sections as needed, such as `Contributing`, `Versioning`, `Authors`, or `Acknowledgments`, depending on the complexity and scale of your project.