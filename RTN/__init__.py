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
from PTN import PTN
from PTN import parse as ptn_parse
from PTT import Parser, add_defaults

from RTN import exceptions, fetch, models, parser, patterns, ranker

from .fetch import check_fetch, check_trash
from .models import BaseRankingModel, DefaultRanking, ParsedData, SettingsModel
from .parser import (
    RTN,
    Torrent,
    batch_parse,
    episodes_from_season,
    get_type,
    parse,
    sort_torrents,
    title_match,
)
from .patterns import check_video_extension, parse_extras
from .ranker import get_rank

__all__ = [
    # Main
    "RTN",
    "Torrent",
    "parse",
    "batch_parse",
    "DefaultRanking",
    "ParsedData",
    # Required Models
    "SettingsModel",
    "BaseRankingModel",
    # PTT
    "Parser",
    "add_defaults",
    # Submodules
    "models",
    "parser",
    "patterns",
    "ranker",
    "fetch",
    "exceptions",
    # Extras
    "PTN",
    "ptn_parse",
    "get_rank",
    "get_type",
    "check_fetch",
    "check_trash",
    "title_match",
    "sort_torrents",
    "parse_extras",
    "episodes_from_season",
    "check_video_extension",
]
