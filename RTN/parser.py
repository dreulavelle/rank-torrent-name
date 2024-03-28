from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, List, Tuple

import Levenshtein
import PTN
import regex
from pydantic import BaseModel, validator

from .fetch import check_fetch
from .models import BaseRankingModel, ParsedData, SettingsModel
from .patterns import parse_extras
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
    """

    raw_title: str
    infohash: str
    data: ParsedData
    fetch: bool = False
    rank: int = 0
    lev_ratio: float = 0.0

    @validator("raw_title", "infohash")
    def validate_strings(cls, v):
        """Ensures raw_title and infohash are strings."""
        if not v or not isinstance(v, str):
            raise TypeError("The title and infohash must be non-empty strings.")
        return v

    @validator("infohash")
    def validate_infohash(cls, v):
        """Validates infohash length and SHA-1 format."""
        if len(v) != 40 or not regex.match(r"^[a-fA-F0-9]{40}$", v):
            raise ValueError("Infohash must be a 40-character SHA-1 hash.")
        return v

    def __eq__(self, other: object) -> bool:
        """Compares Torrent objects based on their infohash."""
        if not isinstance(other, Torrent):
            return False
        return self.infohash == other.infohash


class RTN:
    """
    RTN (Rank Torrent Name) class for parsing and ranking torrent titles based on user preferences.

    Attributes:
        `settings` (SettingsModel): The settings model with user preferences for parsing and ranking torrents.
        `ranking_model` (BaseRankingModel): The model defining the ranking logic and score computation.

    Methods:
        `rank`: Parses a torrent title, computes its rank, and returns a Torrent object with metadata and ranking.
    """

    def __init__(self, settings: SettingsModel, ranking_model: BaseRankingModel):
        """Initializes the RTN class with user settings and a ranking model."""
        if not settings or not ranking_model:
            raise ValueError("Both settings and a ranking model must be provided.")
        if not isinstance(settings, SettingsModel):
            raise TypeError("The settings must be an instance of SettingsModel.")
        if not isinstance(ranking_model, BaseRankingModel):
            raise TypeError("The ranking model must be an instance of BaseRankingModel.")

        self.settings = settings
        self.ranking_model = ranking_model

    def rank(self, raw_title: str, infohash: str) -> Torrent:
        """Parses a torrent title, computes its rank, and returns a Torrent object."""
        if not raw_title or not infohash:
            raise ValueError("Both the title and infohash must be provided.")
        if not isinstance(raw_title, str) or not isinstance(infohash, str):
            raise TypeError("The title and infohash must be strings.")
        if len(infohash) != 40:
            raise ValueError("The infohash must be a valid SHA-1 hash and 40 characters in length.")

        parsed_data = parse(raw_title)
        return Torrent(
            raw_title=raw_title,
            infohash=infohash,
            data=parsed_data,
            fetch=check_fetch(parsed_data, self.settings),
            rank=get_rank(parsed_data, self.settings, self.ranking_model),
            lev_ratio=Levenshtein.ratio(parsed_data.parsed_title.lower(), raw_title.lower()),
        )

    def batch_rank(self, torrents: List[Tuple[str, str]], max_workers: int = 4) -> List[Torrent]:
        """
        Ranks a batch of torrents in parallel using multiple threads.

        Parameters:
            `torrents` (List[Tuple[str, str]]): A list of tuples containing the raw title and infohash of each torrent.
            `max_workers` (int, optional): The maximum number of worker threads to use for parallel processing. Defaults to 4.

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
            >>> len(ranked_torrents)
            3
            >>> isinstance(ranked_torrents[0], Torrent)
            True
            >>> isinstance(ranked_torrents[0].data, ParsedData)
            True
            >>> ranked_torrents[0].fetch
            True
            >>> ranked_torrents[0].rank > 0
            True
            >>> ranked_torrents[0].lev_ratio > 0.0
            True
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(lambda t: self.rank(t[0], t[1]), torrents))


def parse(raw_title: str) -> ParsedData:
    """
    Parses a torrent title using PTN and enriches it with additional metadata extracted from patterns.

    Args:
        raw_title (str): The original torrent title to parse.

    Returns:
        ParsedData: A data model containing the parsed metadata from the torrent title.
    """
    if not raw_title or not isinstance(raw_title, str):
        raise TypeError("The input title must be a non-empty string.")

    parsed_dict: dict[str, Any] = PTN.parse(raw_title, coherent_types=True)
    parsed_dict["year"] = parsed_dict["year"][0] if parsed_dict.get("year") else 0
    extras: dict[str, Any] = parse_extras(raw_title)
    full_data = {**parsed_dict, **extras}  # Merge PTN parsed data with RTN extras.
    full_data["raw_title"] = raw_title
    full_data["parsed_title"] = parsed_dict.get("title")
    return ParsedData(**full_data)


def parse_chunk(chunk: List[str]) -> List[ParsedData]:
    """
    Parses a chunk of torrent titles.

    Args:
        chunk (List[str]): A list of torrent titles to parse.

    Returns:
        List[ParsedData]: A list of ParsedData objects containing the parsed metadata from the torrent titles.
    """
    return [parse(title) for title in chunk]


def batch_parse(titles: List[str], chunk_size: int = 50, max_workers: int = 4) -> List[ParsedData]:
    """
    Parses a list of torrent titles in batches for improved performance.

    Args:
        titles (List[str]): A list of torrent titles to parse.
        chunk_size (int): The number of titles to process in each batch.
        max_workers (int): The maximum number of worker threads to use for parsing.

    Returns:
        List[ParsedData]: A list of ParsedData objects for each title.
    """
    chunks = [titles[i : i + chunk_size] for i in range(0, len(titles), chunk_size)]
    parsed_data = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chunk = {executor.submit(parse_chunk, chunk): chunk for chunk in chunks}
        for future in as_completed(future_to_chunk):
            chunk_result = future.result()
            parsed_data.extend(chunk_result)
    return parsed_data


def title_match(correct_title: str, raw_title: str, threshold: float = 0.9) -> bool:
    """
    Compares two titles using the Levenshtein ratio to determine similarity.

    Args:
        correct_title (str): The reference title to compare against.
        raw_title (str): The title to compare with the reference title.
        threshold (float): The similarity threshold to consider the titles as matching.

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


def sort(torrents: List[Torrent]) -> List[Torrent]:
    """
    Sorts a list of Torrent objects based on their rank in descending order.

    Args:
        torrents (List[Torrent]): The list of Torrent objects to sort.

    Returns:
        List[Torrent]: The sorted list of Torrent objects by rank.
    """
    return sorted(torrents, key=lambda t: t.rank, reverse=True)
