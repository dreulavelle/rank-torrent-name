<div align="center">

<h1>🏆 Rank Torrent Name 🏆</h1>

<p align="center">
  <a href="https://codecov.io/gh/dreulavelle/rank-torrent-name">
    <img src="https://codecov.io/gh/dreulavelle/rank-torrent-name/graph/badge.svg" alt="Code Coverage"/>
  </a>
  <a href="https://badge.fury.io/py/rank-torrent-name">
    <img src="https://badge.fury.io/py/rank-torrent-name.svg" alt="PyPI version"/>
  </a>
  <img src="https://img.shields.io/github/actions/workflow/status/dreulavelle/rank-torrent-name/battery.yml" alt="GitHub Actions Workflow Status"/>
  <img src="https://img.shields.io/github/license/dreulavelle/rank-torrent-name" alt="GitHub License"/>
</p>

<p align="center">
  <strong>Elevate Your Torrent Game</strong>
</p>

</div>

<hr>

**Rank Torrent Name (RTN)** is a powerful Python library that revolutionizes the way you handle torrent names. With its advanced parsing and customizable ranking system, RTN empowers users to effortlessly filter and prioritize torrents based on their specific preferences.

> 💡 RTN serves as a comprehensive Version and Ranking System, perfect for parsing and scoring scraped torrent results with precision and flexibility.

## 🌟 Key Features

- **🔍 Smart Torrent Parsing:** Leverages [Parsett](https://github.com/dreulavelle/ptt) for in-depth metadata extraction and enhancement.
- **🏆 Customizable Ranking:** Tailor your torrent selection criteria with user-defined preferences for quality, resolution, audio, and more.
- **🎯 Precision Filtering:** Easily set requirements, exclusions, and preferences to pinpoint your ideal torrents.
- **📊 Flexible Ranking Model:** Utilize the default model or create your own to match your unique needs.
- **🔤 Title Accuracy Check:** Employs Levenshtein Ratio Comparison to ensure parsed titles match originals.

## 🛠️ Core Functionality

RTN offers a comprehensive toolkit for torrent management:

- **Parsing:** Decode torrent names with advanced algorithms.
- **Ranking:** Evaluate torrents based on your custom criteria.
- **Extensibility:** Leverage submodules for enhanced capabilities.
- **Utility Functions:** Streamline data fetching and sorting processes.

## 📚 Module Overview

### Main Components
- `RTN`: The central class for parsing and ranking operations.
- `Torrent`: Data structure for parsed torrent information.
- `parse`: Functions for individual torrent parsing.
- `DefaultRanking`: Standard model for torrent rank calculation.
- `ParsedData`: Structured storage for parsed torrent details.

### Essential Models for Ranking
- `SettingsModel`: Customizable user preferences storage.
- `BaseRankingModel`: Foundation for torrent rank calculations.

### Submodules
- `models`: Additional data structures for ranking.
- `parser`: Enhanced parsing tools.
- `patterns`: Expanded parsing pattern utilities.
- `ranker`: Advanced ranking functionalities.
- `fetch`: Data retrieval and validation utilities.
- `exceptions`: Custom error handling mechanisms.

### Extra Utilities
- `get_rank`: Calculate parsed data rankings.
- `check_fetch`: Determine torrent fetch eligibility.
- `trash_handler`: Identify and filter low-quality torrents.
- `title_match`: Accurate torrent title comparison.
- `sort_torrents`: Rank-based torrent sorting.
- `parse_extras`: Extract additional torrent metadata.
- `episodes_from_season`: Generate episode titles for entire seasons.

📘 For a deeper dive, check out our [Getting Started](./Users/FAQ.md) guide for users or the [Developers](./Developers/Developers.md) section for technical insights.