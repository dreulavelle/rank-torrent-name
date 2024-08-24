"""
Welcome to RTN (Rank Torrent Name)! 🎉

This package provides tools for parsing, analyzing, and ranking torrent names based on user-defined criteria. It includes functionality for:

- Main parsing and ranking operations.
- Models for configuring the ranking behavior.
- Submodules for advanced manipulation and extension.
- PTN Integration for additional parsing capabilities.
- Additional utility functions for fetching and sorting data.

Importable modules and classes are categorized below for ease of use.

Main:
    - `RTN`: Main class for parsing and ranking torrent names.
    - `Torrent`: Data class for storing parsed torrent information.
    - `parse`: Parse a single torrent name.
    - `batch_parse`: Parse multiple torrent names in batches.
    - `DefaultRanking`: Default ranking model for calculating torrent ranks.
    - `ParsedData`: Data class for storing parsed torrent information.

Required Models:
    - `SettingsModel`: Model for storing user settings.
    - `BaseRankingModel`: Base model for calculating torrent ranks.

Submodules:
    - `models`: Additional models for storing ranking data.
    - `parser`: Additional parsing utilities and functions.
    - `patterns`: Additional parsing patterns and utilities.
    - `ranker`: Additional ranking utilities and functions.
    - `fetch`: Additional fetching and checking utilities.
    - `exceptions`: Custom exceptions for handling errors.

Extras:
    - `PTN`: Package for parsing torrent names.
    - `ptn_parse`: Function for parsing torrent names using PTN.
    - `get_rank`: Function for calculating the rank of parsed data.
    - `check_fetch`: Function for checking if a torrent should be fetched.
    - `check_trash`: Function for checking if a torrent is trash.
    - `title_match`: Function for matching torrent titles.
    - `sort_torrents`: Function for sorting torrents based on rank.
    - `parse_extras`: Function for parsing additional torrent information.
    - `episodes_from_season`: Function for generating episode titles from a season.

For more information on each module or class, refer to the respective docstrings.
"""

from PTT import Parser, add_defaults, parse_title

from RTN import exceptions, fetch, models, parser, patterns, ranker

from .extras import episodes_from_season, get_lev_ratio, sort_torrents, title_match
from .fetch import check_fetch
from .models import BaseRankingModel, DefaultRanking, ParsedData, SettingsModel
from .parser import RTN, Torrent, parse
from .patterns import check_pattern, check_video_extension, normalize_title
from .ranker import get_rank

__all__ = [
    # Main
    "RTN",
    "Torrent",
    "parse",
    "DefaultRanking",
    "ParsedData",
    # Required Models
    "SettingsModel",
    "BaseRankingModel",
    # PTT
    "Parser",
    "add_defaults",
    "parse_title",
    # Submodules
    "models",
    "parser",
    "patterns",
    "ranker",
    "fetch",
    "exceptions",
    # Patterns
    "normalize_title",
    "check_video_extension",
    "check_pattern",
    # Extras
    "title_match",
    "get_lev_ratio",
    "sort_torrents",
    "get_rank",
    "check_fetch",
    "episodes_from_season",
]
