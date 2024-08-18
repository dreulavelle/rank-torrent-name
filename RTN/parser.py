"""
Parser module for parsing torrent titles and extracting metadata using RTN patterns.

The module provides functions for parsing torrent titles, extracting metadata, and ranking torrents based on user preferences.

Functions:
- `parse`: Parse a torrent title and enrich it with additional metadata.

Classes:
- `Torrent`: Represents a torrent with metadata parsed from its title and additional computed properties.
- `RTN`: Rank Torrent Name class for parsing and ranking torrent titles based on user preferences.

For more information on each function or class, refer to the respective docstrings.

Example:
    >>> from RTN import parse, Torrent
    >>> data = parse("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]")
    >>> isinstance(data, ParsedData)
    True
    >>> torrent = Torrent(
    ...     raw_title="The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]",
    ...     infohash="c08a9ee8ce3a5c2c08865e2b05406273cabc97e7",
    ...     data=data,
    ...     fetch=True,
    ...     rank=500,
    ...     lev_ratio=0.95,
    ... )
    >>> torrent.raw_title
    'The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]'
    >>> torrent.infohash
    'c08a9ee8ce3a5c2c08865e2b05406273cabc97e7'
    >>> torrent.data.parsed_title
    'The Walking Dead'
    >>> torrent.fetch
    True
    >>> torrent.rank
    500
    >>> torrent.lev_ratio
    0.95
"""
from typing import Any, Dict, List
from PTT import parse_title

from .exceptions import GarbageTorrent
from .extras import get_lev_ratio, title_match
from .fetch import check_fetch
from .models import BaseRankingModel, ParsedData, SettingsModel, Torrent
from .patterns import normalize_title
from .ranker import get_rank


class RTN:
    """
    RTN (Rank Torrent Name) class for parsing and ranking torrent titles based on user preferences.

    Attributes:
        `settings` (SettingsModel): The settings model with user preferences for parsing and ranking torrents.
        `ranking_model` (BaseRankingModel): The model defining the ranking logic and score computation.
        `lev_threshold` (float): The Levenshtein ratio threshold for title matching. Defaults to 0.9.

    Methods:
        `rank`: Parses a torrent title, computes its rank, and returns a Torrent object with metadata and ranking.
    """

    def __init__(self, settings: SettingsModel, ranking_model: BaseRankingModel, lev_threshold: float = 0.9):
        """
        Initializes the RTN class with settings and a ranking model.

        Parameters:
            `settings` (SettingsModel): The settings model with user preferences for parsing and ranking torrents.
            `ranking_model` (BaseRankingModel): The model defining the ranking logic and score computation.
            `lev_threshold` (float): The Levenshtein ratio threshold for title matching. Defaults to 0.9.
        
        Raises:
            ValueError: If settings or a ranking model is not provided.
            TypeError: If settings is not an instance of SettingsModel or the ranking model is not an instance of BaseRankingModel.

        Example:
            >>> from RTN import RTN
            >>> from RTN.models import SettingsModel, DefaultRanking
            >>>
            >>> settings_model = SettingsModel()
            >>> ranking_model = DefaultRanking()
            >>> rtn = RTN(settings_model, ranking_model, lev_threshold=0.94)
        """
        if not settings or not ranking_model:
            raise ValueError("Both settings and a ranking model must be provided.")
        if not isinstance(settings, SettingsModel):
            raise TypeError("The settings must be an instance of SettingsModel.")
        if not isinstance(ranking_model, BaseRankingModel):
            raise TypeError("The ranking model must be an instance of BaseRankingModel.")

        self.settings = settings
        self.ranking_model = ranking_model
        self.lev_threshold = lev_threshold

    def rank(self, raw_title: str, infohash: str, correct_title: str = "", remove_trash: bool = False) -> Torrent:
        """
        Parses a torrent title, computes its rank, and returns a Torrent object with metadata and ranking.

        Parameters:
            `raw_title` (str): The original title of the torrent to parse.
            `infohash` (str): The SHA-1 hash identifier of the torrent.
            `correct_title` (str): The correct title to compare against for similarity. Defaults to an empty string.
            `remove_trash` (bool): Whether to check for trash patterns and raise an error if found. Defaults to True.

        Returns:
            Torrent: A Torrent object with metadata and ranking information.

        Raises:
            ValueError: If the title or infohash is not provided for any torrent.
            TypeError: If the title or infohash is not a string.
            GarbageTorrent: If the title is identified as trash and should be ignored by the scraper, or invalid SHA-1 infohash is given.

        Notes:
            - If `correct_title` is provided, the Levenshtein ratio will be calculated between the parsed title and the correct title.
            - If the ratio is below the threshold, a `GarbageTorrent` error will be raised.
            - If no correct title is provided, the Levenshtein ratio will be set to 0.0.

        Example:
            >>> rtn = RTN(settings_model, ranking_model)
            >>> torrent = rtn.rank("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7")
            >>> isinstance(torrent, Torrent)
            True
            >>> isinstance(torrent.data, ParsedData)
            True
            >>> torrent.fetch
            True
            >>> torrent.rank > 0
            True
            >>> torrent.lev_ratio > 0.0
            True
        """
        if not raw_title or not infohash:
            raise ValueError("Both the title and infohash must be provided.")
        if not isinstance(raw_title, str) or not isinstance(infohash, str):
            raise TypeError("The title and infohash must be strings.")
        if not isinstance(correct_title, str):
            raise TypeError("The correct title must be a string.")
        if len(infohash) != 40:
            raise GarbageTorrent("The infohash must be a valid SHA-1 hash and 40 characters in length.")

        parsed_data: ParsedData = parse(raw_title)

        if self.settings.options.remove_trash:
            if parsed_data.trash:
                raise GarbageTorrent("This title is trash and should be ignored by the scraper.")

        if correct_title:
            lev_ratio: float = get_lev_ratio(correct_title, parsed_data.parsed_title, self.lev_threshold)

        if remove_trash and lev_ratio < self.lev_threshold:
            raise GarbageTorrent(f"This title does not match the correct title, got ratio of {lev_ratio}")

        fetch: bool = check_fetch(parsed_data, self.settings)
        rank: int = get_rank(parsed_data, self.settings, self.ranking_model)

        return Torrent(
            infohash=infohash,
            raw_title=raw_title,
            cleaned_title=normalize_title(parsed_data.parsed_title),
            data=parsed_data,
            fetch=fetch,
            rank=rank,
            lev_ratio=lev_ratio or 0.0
        )


def parse(raw_title: str, json: bool = False) -> ParsedData:
    """
    Parses a torrent title using PTN and enriches it with additional metadata extracted from patterns.

    Args:
        `raw_title` (str): The original torrent title to parse.
        `remove_trash` (bool): Whether to check for trash patterns and raise an error if found. Defaults to True.

    Returns:
        ParsedData: A data model containing the parsed metadata from the torrent title.
    """
    if not raw_title or not isinstance(raw_title, str):
        raise TypeError("The input title must be a non-empty string.")

    data: Dict[str, Any] = parse_title(raw_title)
    item = ParsedData(
        **data,
        raw_title=raw_title,
        parsed_title=data.get("title", "")
    )

    return item if not json else item.to_dict()


def parse_chunk(chunk: List[str]) -> List[ParsedData]:
    """
    Parses a chunk of torrent titles.

    Args:
        `chunk` (List[str]): A list of torrent titles to parse.
        `remove_trash` (bool): Whether to check for trash patterns and raise an error if found. Defaults to True.

    Returns:
        List[ParsedData]: A list of ParsedData objects containing the parsed metadata from the torrent titles.
    """
    return [parse(title) for title in chunk]


def batch_parse(titles: List[str], chunk_size: int = 50) -> List[ParsedData]:
    """
    Parses a list of torrent titles in batches for improved performance.

    Args:
        `titles` (List[str]): A list of torrent titles to parse.
        `chunk_size` (int): The number of titles to process in each batch.
        `remove_trash` (bool): Whether to check for trash patterns and raise an error if found. Defaults to True.

    Returns:
        List[ParsedData]: A list of ParsedData objects for each title.
    """
    chunks = [titles[i : i + chunk_size] for i in range(0, len(titles), chunk_size)]
    parsed_data = []
    for chunk in chunks:
        chunk_result = parse_chunk(chunk)
        parsed_data.extend(chunk_result)
    return parsed_data
