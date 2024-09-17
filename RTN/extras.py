"""
Extras module for additional functionality related to RTN processing.

Functions:
    - `title_match`: Compare two titles using the Levenshtein ratio to determine similarity.
    - `sort_torrents`: Sort a set of Torrent objects by their resolution and rank in descending order.
    - `extract_seasons`: Extract season numbers from the title.
    - `extract_episodes`: Extract episode numbers from the title.
    - `episodes_from_season`: Extract episode numbers for a specific season from the title.

For more details, please refer to the documentation.
"""

from typing import Any, Dict, List, Set

from Levenshtein import ratio
from PTT import parse_title

from .models import Resolution, Torrent
from .patterns import normalize_title


def title_match(correct_title: str, parsed_title: str, threshold: float = 0.85) -> bool:
    """
    Compares two titles using the Levenshtein ratio to determine similarity.

    Args:
        `correct_title` (str): The reference title to compare against.
        `parsed_title` (str): The title to compare with the reference title.
        `threshold` (float): The similarity threshold to consider the titles as matching.

    Returns:
        `bool`: True if the titles match, False otherwise.
    """
    check = get_lev_ratio(correct_title, parsed_title, threshold)
    return check >= threshold


def get_lev_ratio(correct_title: str, parsed_title: str, threshold: float = 0.85) -> float:
    """
    Compares two titles using the Levenshtein ratio to determine similarity.

    Args:
        `correct_title` (str): The reference title to compare against.
        `parsed_title` (str): The title to compare with the reference title.
        `threshold` (float): The similarity threshold to consider the titles as matching.

    Returns:
        `float`: The Levenshtein ratio between the two titles.
    """
    if not (correct_title or parsed_title):
        raise ValueError("Both titles must be provided.")
    if not isinstance(correct_title, str) or not isinstance(parsed_title, str):
        raise TypeError("Both titles must be strings.")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError("The threshold must be a number between 0 and 1.")

    normalized_correct_title = normalize_title(correct_title)
    normalized_parsed_title = normalize_title(parsed_title)
    lev_ratio: float = ratio(normalized_correct_title, normalized_parsed_title, score_cutoff=threshold)
    return round(lev_ratio, 3)


def sort_torrents(torrents: Set[Torrent]) -> Dict[str, Torrent]:
    """
    Sorts a set of Torrent objects by their resolution bucket and then by their rank in descending order.
    Returns a dictionary with infohash as keys and Torrent objects as values.

    Args:
        `torrents` (Set[Torrent]): A set of Torrent objects.

    Raises:
        `TypeError`: If the input is not a set of Torrent objects.

    Returns:
        `Dict[str, Torrent]`: A dictionary of Torrent objects sorted by resolution and rank in descending order,
        with the torrent's infohash as the key.
    """

    if not isinstance(torrents, set) or not all(isinstance(t, Torrent) for t in torrents):
        raise TypeError("The input must be a set of Torrent objects.")

    buckets = {
        Resolution.UHD: 4,
        Resolution.UHD_2160P: 4,
        Resolution.UHD_1440P: 4,
        Resolution.FHD: 3,
        Resolution.HD: 2,
        Resolution.SD_576P: 1,
        Resolution.SD_480P: 1,
        Resolution.SD_360P: 1,
        Resolution.UNKNOWN: 0,
    }

    def get_bucket(torrent: Torrent) -> int:
        resolution_map = {
            "4k": Resolution.UHD,
            "2160p": Resolution.UHD_2160P,
            "1440p": Resolution.UHD_1440P,
            "1080p": Resolution.FHD,
            "720p": Resolution.HD,
            "576p": Resolution.SD_576P,
            "480p": Resolution.SD_480P,
            "360p": Resolution.SD_360P,
            "unknown": Resolution.UNKNOWN,
        }
        resolution = resolution_map.get(torrent.data.resolution, Resolution.UNKNOWN)
        return buckets[resolution]

    sorted_torrents: List[Torrent] = sorted(
        torrents,
        key=lambda torrent: (get_bucket(torrent), torrent.rank if torrent.rank is not None else float("-inf")),
        reverse=True
    )

    return {torrent.infohash: torrent for torrent in sorted_torrents}


def extract_seasons(raw_title: str) -> List[int]:
    """
    Extract season numbers from the title or filename.

    Args:
        `raw_title` (str): The original title of the torrent to analyze.

    Returns:
        `List[int]`: A list of extracted season numbers from the title.
    """
    if not raw_title or not isinstance(raw_title, str):
        raise TypeError("The input title must be a non-empty string.")
    return parse_title(raw_title)["seasons"]


def extract_episodes(raw_title: str) -> List[int]:
    """
    Extract episode numbers from the title or filename.

    Args:
        `raw_title` (str): The original title of the torrent to analyze.

    Returns:
        `List[int]`: A list of extracted episode numbers from the title.
    """
    if not raw_title or not isinstance(raw_title, str):
        raise TypeError("The input title must be a non-empty string.")
    return parse_title(raw_title)["episodes"]


def episodes_from_season(raw_title: str, season_num: int) -> List[int]:
    """
    Only return episode numbers if the season number is found in the title
    and the season number matches the input season number.

    Args:
        `raw_title` (str): The original title of the torrent to analyze.
        `season_num` (int): The season number to extract episodes for.

    Returns:
        `List[int]`: A list of extracted episode numbers for the specified season.
    """
    if not season_num:
        raise ValueError("The season number must be provided.")
    if not isinstance(season_num, int) or season_num <= 0:
        raise TypeError("The season number must be a positive integer.")
    if not raw_title or not isinstance(raw_title, str):
        raise ValueError("The input title must be a non-empty string.")

    data: dict[str, Any] = parse_title(raw_title)

    season_from_title = data.get("seasons", [])
    episodes_from_title = data.get("episodes", [])

    if isinstance(episodes_from_title, list) and season_num in season_from_title:
        return episodes_from_title
    return []
