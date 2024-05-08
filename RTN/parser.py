"""
Parser module for parsing torrent titles and extracting metadata using PTN and RTN patterns.

The module provides functions for parsing torrent titles, extracting metadata, and ranking torrents based on user preferences.

Functions:
- `parse`: Parse a torrent title using PTN and enrich it with additional metadata extracted from patterns.
- `parse_chunk`: Parse a chunk of torrent titles.
- `batch_parse`: Parse a list of torrent titles in batches for improved performance.
- `title_match`: Compare two titles using the Levenshtein ratio to determine similarity.
- `sort_torrents`: Sort a set of Torrent objects by their rank in descending order.
- `is_movie`: Determine if the item is a movie based on the absence of typical show indicators.
- `get_type`: Determine the type of media based on the parsed data.
- `episodes_from_season`: Extract episode numbers for a specific season from the title.

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
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Set, Tuple

import Levenshtein
import PTN
import regex
from PTT import Parser, add_defaults
from pydantic import BaseModel, field_validator

from RTN.exceptions import GarbageTorrent

from .fetch import check_fetch, check_trash
from .models import BaseRankingModel, ParsedData, SettingsModel
from .patterns import IS_MOVIE_COMPILED, extract_episodes, parse_extras
from .ranker import get_rank


class Torrent(BaseModel):
    """
    Represents a torrent with metadata parsed from its title and additional computed properties.

    Attributes:
        `raw_title` (str): The original title of the torrent.
        `infohash` (str): The SHA-1 hash identifier of the torrent.
        `data` (ParsedData): Metadata extracted from the torrent title including PTN parsing and additional extras.
        `fetch` (bool): Indicates whether the torrent meets the criteria for fetching based on user settings.
        `rank` (int): The computed ranking score of the torrent based on user-defined preferences.
        `lev_ratio` (float): The Levenshtein ratio comparing the parsed title and the raw title for similarity.

    Methods:
        __eq__: Determines equality based on the infohash of the torrent, allowing for easy comparison.
        __hash__: Generates a hash based on the infohash of the torrent for set operations.
    
    Raises:
        `GarbageTorrent`: If the title is identified as trash and should be ignored by the scraper.

    Example:
        >>> torrent = Torrent(
        ...     raw_title="The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]",
        ...     infohash="c08a9ee8ce3a5c2c08865e2b05406273cabc97e7",
        ...     data=ParsedData(...),
        ...     fetch=True,
        ...     rank=500,
        ...     lev_ratio=0.95,
        ... )
        >>> isinstance(torrent, Torrent)
        True
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

    raw_title: str
    infohash: str
    data: ParsedData
    fetch: bool = False
    rank: int = 0
    lev_ratio: float = 0.0

    class Config:
        frozen = True

    @field_validator("infohash")
    def validate_infohash(cls, v):
        """Validates infohash length and SHA-1 format."""
        if len(v) != 40 or not regex.match(r"^[a-fA-F0-9]{40}$", v):
            raise GarbageTorrent("Infohash must be a 40-character SHA-1 hash.")
        return v

    def __eq__(self, other: object) -> bool:
        """Compares Torrent objects based on their infohash."""
        return isinstance(other, Torrent) and self.infohash == other.infohash

    def __hash__(self) -> int:
        return hash(self.infohash)


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

        if remove_trash: # noqa: SIM102
            if check_trash(raw_title):
                raise GarbageTorrent("This title is trash and should be ignored by the scraper.")

        parsed_data = parse(raw_title, remove_trash)
        lev_ratio = Levenshtein.ratio(parsed_data.parsed_title.lower(), correct_title.lower())

        if correct_title: # noqa: SIM102
            if remove_trash and lev_ratio < self.lev_threshold:
                raise GarbageTorrent(f"This title does not match the correct title, got ratio of {lev_ratio:.3f}")

        fetch = check_fetch(parsed_data, self.settings)
        parsed_data.fetch = fetch
        rank = get_rank(parsed_data, self.settings, self.ranking_model)

        return Torrent(
            raw_title=raw_title,
            infohash=infohash,
            data=parsed_data,
            fetch=fetch,
            rank=rank,
            lev_ratio=lev_ratio
        )

    def batch_rank(self, torrents: List[Tuple[str, str]], correct_title: str = "", remove_trash: bool = False, max_workers: int = 4) -> List[Torrent]:
        """
        Ranks a batch of torrents in parallel using multiple threads.

        Parameters:
            `torrents` (List[Tuple[str, str]]): A list of tuples containing the raw title and infohash of each torrent.
            `max_workers` (int, optional): The maximum number of worker threads to use for parallel processing. Defaults to 4.
            `correct_title` (str): The correct title to compare against for similarity. Defaults to an empty string.
            `remove_trash` (bool): Whether to check for trash patterns and raise an error if found. Defaults to True.

        Returns:
            List[Torrent]: A list of Torrent objects representing the ranked torrents.

        Raises:
            ValueError: If the title or infohash is not provided for any torrent.
            TypeError: If the title or infohash is not a string.
            ValueError: If the infohash is not a valid SHA-1 hash and 40 characters in length.

        Example:
            >>> torrents = [
            ...     ("The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e7"),
            ...     ("Example.Movie.2020.1080p.BluRay.x264-Example", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e8"),
            ...     ("Example.Series.S2.2020", "c08a9ee8ce3a5c2c08865e2b05406273cabc97e9"),
            ... ]

            >>> rtn = RTN(settings_model, ranking_model)
            >>> ranked_torrents = rtn.batch_rank(torrents)
            >>> isinstance(ranked_torrents, list)
            True
            >>> all(isinstance(t, Torrent) for t in ranked_torrents)
            True
            >>> all(t.rank > 0 for t in ranked_torrents)
            True
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(lambda t: self.rank(t[0], t[1], correct_title=correct_title, remove_trash=remove_trash), torrents))


def parse(raw_title: str, remove_trash: bool = False) -> ParsedData:
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

    if remove_trash:  # noqa: SIM102
        if check_trash(raw_title):
            raise GarbageTorrent("This title is trash and should be ignored by the scraper.")

    data = PTN.parse(raw_title, coherent_types=True)
    extras = parse_extras(raw_title)

    ptn_data = ParsedData(
        # PTN
        raw_title=raw_title,
        parsed_title=data.get("title", ""),
        year=data.get("year", 0)[0] if data.get("year") else 0,
        resolution=data.get("resolution", []),
        quality=data.get("quality", []),
        season=data.get("season", []),
        episode=data.get("episode", []),
        codec=data.get("codec", []),
        audio=data.get("audio", []),
        subtitles=data.get("subtitles", []),
        language=data.get("language", []),
        bitDepth=data.get("bitDepth", []),
        proper=data.get("proper", False),
        repack=data.get("repack", False),
        remux=data.get("remux", False),
        upscaled=data.get("upscaled", False),
        remastered=data.get("remastered", False),
        directorsCut=data.get("directorsCut", False),
        extended=data.get("extended", False),
        # Extras
        is_multi_audio=extras.get("is_multi_audio", False),
        is_multi_subtitle=extras.get("is_multi_subtitle", False),
        is_complete=extras.get("is_complete", False),
        is_4k=extras.get("is_4k", False),
        hdr=extras.get("hdr", ""),
    )

    # Check both PTT and PTN for episode data.
    if not ptn_data.episode and ptn_data.type == "show":
        ptn_data.episode = extras.get("episode", [])

    return ptn_data


def parse_chunk(chunk: List[str], remove_trash: bool) -> List[ParsedData]:
    """
    Parses a chunk of torrent titles.

    Args:
        `chunk` (List[str]): A list of torrent titles to parse.
        `remove_trash` (bool): Whether to check for trash patterns and raise an error if found. Defaults to True.

    Returns:
        List[ParsedData]: A list of ParsedData objects containing the parsed metadata from the torrent titles.
    """
    return [parse(title, remove_trash) for title in chunk]


def batch_parse(titles: List[str], remove_trash: bool = True, chunk_size: int = 50, max_workers: int = 4) -> List[ParsedData]:
    """
    Parses a list of torrent titles in batches for improved performance.

    Args:
        `titles` (List[str]): A list of torrent titles to parse.
        `chunk_size` (int): The number of titles to process in each batch.
        `max_workers` (int): The maximum number of worker threads to use for parsing.
        `remove_trash` (bool): Whether to check for trash patterns and raise an error if found. Defaults to True.

    Returns:
        List[ParsedData]: A list of ParsedData objects for each title.
    """
    chunks = [titles[i : i + chunk_size] for i in range(0, len(titles), chunk_size)]
    parsed_data = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chunk = {executor.submit(parse_chunk, chunk, remove_trash): chunk for chunk in chunks}
        for future in as_completed(future_to_chunk):
            chunk_result = future.result()
            parsed_data.extend(chunk_result)
    return parsed_data


def title_match(correct_title: str, raw_title: str, threshold: float = 0.9) -> bool:
    """
    Compares two titles using the Levenshtein ratio to determine similarity.

    Args:
        `correct_title` (str): The reference title to compare against.
        `raw_title` (str): The title to compare with the reference title.
        `threshold` (float): The similarity threshold to consider the titles as matching.

    Returns:
        bool: True if the titles are similar above the specified threshold; False otherwise.
    """
    if not (correct_title or raw_title):
        raise ValueError("Both titles must be provided.")
    if not isinstance(correct_title, str) or not isinstance(raw_title, str):
        raise TypeError("Both titles must be strings.")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError("The threshold must be a float between 0 and 1.")
    return Levenshtein.ratio(correct_title.lower(), raw_title.lower()) >= threshold


def sort_torrents(torrents: Set[Torrent]) -> Dict[str, Torrent]:
    """
    Sorts a set of Torrent objects by their rank in descending order and returns a dictionary
    with infohash as keys and Torrent objects as values.

    Parameters:
    - `torrents`: A set of Torrent objects.

    Returns:
    - A dictionary of Torrent objects sorted by rank in descending order, with the torrent's
      infohash as the key.
    """
    if not isinstance(torrents, set) or not all(isinstance(t, Torrent) for t in torrents):
        raise TypeError("The input must be a set of Torrent objects.")
    sorted_torrents: List[Torrent] = sorted(torrents, key=lambda torrent: torrent.rank, reverse=True)
    return {torrent.infohash: torrent for torrent in sorted_torrents}


def is_movie(data: ParsedData) -> bool:
    """
    Determine if the item is a movie based on the absence of typical show indicators in the title,
    the absence of an episode number, and specific year considerations.

    Parameters:
    - `data`: ParsedData instance containing information about the item, including `raw_title`, `year`, and `episode`.

    Returns:
    - bool: True if the item is likely a movie, False otherwise.

    Raises:
    - ValueError: If no parsed data is provided.
    """
    if not isinstance(data, ParsedData):
        raise TypeError("Parsed data must be provided.")
    if not data.raw_title:
        raise ValueError("The raw title must be a non-empty string.")
    return not any(pattern.search(data.raw_title) for pattern in IS_MOVIE_COMPILED) and not data.episode and data.year != 0


def get_type(data: ParsedData) -> str:
    """
    Determine the type of media based on the parsed data.

    Parameters:
    - `data`: ParsedData instance containing information about the item, including `raw_title`.

    Returns:
    - str: The type of media based on the parsed data. "movie" if it's a movie, "show" otherwise.

    Raises:
    - ValueError: If no parsed data is provided.
    """
    if is_movie(data):
        return "movie"
    return "show"


def episodes_from_season(raw_title: str, season_num: int) -> List[int]:
    """
    Only return episode numbers if the season number is found in the title
    and the season number matches the input season number.

    Parameters:
    - `raw_title` (str): The original title of the torrent to analyze.
    - `season_num` (int): The season number to extract episodes for.

    Returns:
    - List[int]: A list of extracted episode numbers for the specified season.
    """
    if not season_num:
        raise ValueError("The season number must be provided.")
    if not isinstance(season_num, int) or season_num <= 0:
        raise TypeError("The season number must be a positive integer.")
    if not raw_title or not isinstance(raw_title, str):
        raise ValueError("The input title must be a non-empty string.")

    data: dict[str, Any] = PTN.parse(raw_title, coherent_types=True)

    season_from_title = data.get("season", [])
    if isinstance(season_from_title, int):
        season_from_title = [season_from_title]
    elif not isinstance(season_from_title, list):
        season_from_title = []

    if season_num in season_from_title:
        eps = extract_episodes(raw_title)
        if isinstance(eps, list) and len(eps) > 0:
            return eps
    return []

def parsett(query: str) -> dict:
    """
    Parse a torrent title using the default PTT parser with additional patterns and settings.

    Parameters:
    - `query` (str): The torrent title to parse.

    Returns:
    - dict: A dictionary containing the parsed metadata from the torrent title.
    """
    p = Parser()
    add_defaults(p)
    return p.parse(query)