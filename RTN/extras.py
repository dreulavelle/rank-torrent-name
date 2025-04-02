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

from enum import Enum
from typing import Any, Dict, List, Set

from Levenshtein import ratio
from PTT import parse_title

from .models import Torrent
from .patterns import normalize_title


class Resolution(Enum):
    UHD_2160P = 9
    UHD_1440P = 7
    FHD_1080P = 6
    HD_720P = 5
    SD_576P = 4
    SD_480P = 3
    SD_360P = 2
    UNKNOWN = 1


RESOLUTION_MAP: dict[str, Resolution] = {
    "4k": Resolution.UHD_2160P,
    "2160p": Resolution.UHD_2160P,
    "1440p": Resolution.UHD_1440P,
    "1080p": Resolution.FHD_1080P,
    "720p": Resolution.HD_720P,
    "576p": Resolution.SD_576P,
    "480p": Resolution.SD_480P,
    "360p": Resolution.SD_360P,
    "unknown": Resolution.UNKNOWN,
}


def get_resolution(torrent: Torrent) -> Resolution:
    """
    Get the resolution of a torrent.

    Args:
        `torrent` (Torrent): The torrent object to get the resolution of.

    Returns:
        `Resolution`: The resolution of the torrent.
    """
    return RESOLUTION_MAP.get(torrent.data.resolution.lower(), Resolution.UNKNOWN)


def title_match(correct_title: str, parsed_title: str, threshold: float = 0.85, aliases: dict = {}) -> bool:
    """
    Compares two titles using the Levenshtein ratio to determine similarity.

    Args:
        `correct_title` (str): The reference title to compare against.
        `parsed_title` (str): The title to compare with the reference title.
        `threshold` (float): The similarity threshold to consider the titles as matching.
        `aliases` (dict, optional): A dictionary of aliases for the correct title.
    Returns:
        `bool`: True if the titles match, False otherwise.
    """
    check = get_lev_ratio(correct_title, parsed_title, threshold, aliases)
    return check >= threshold


def get_lev_ratio(correct_title: str, parsed_title: str, threshold: float = 0.85, aliases: dict = {}) -> float:
    """
    Compares two titles using the Levenshtein ratio to determine similarity.

    Args:
        `correct_title` (str): The reference title to compare against.
        `parsed_title` (str): The title to compare with the reference title.
        `threshold` (float): The similarity threshold to consider the titles as matching.
        `aliases` (dict, optional): A dictionary of aliases for the correct title.

    Returns:
        `float`: The highest Levenshtein ratio between the parsed title and any of the correct titles (including aliases if provided).
    """
    if not (correct_title and parsed_title):
        raise ValueError("Both titles must be provided.")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError("The threshold must be a number between 0 and 1.")

    ratio_set = {
        ratio(normalize_title(title), normalize_title(parsed_title), score_cutoff=threshold)
        for title in [normalize_title(correct_title)] + [normalize_title(alias) for alias_list in aliases.values() for alias in alias_list]
    }

    return max(ratio_set)


def sort_torrents(torrents: Set[Torrent], bucket_limit: int = None, resolutions: list[Resolution] = []) -> Dict[str, Torrent]:
    """
    Sorts a set of Torrent objects by their resolution bucket and then by their rank in descending order.
    Returns a dictionary with infohash as keys and Torrent objects as values.

    Args:
        `torrents` (Set[Torrent]): A set of Torrent objects.
        `bucket_limit` (int, optional): The maximum number of torrents to return from each bucket.
        `resolutions` (list[Resolution], optional): A list of resolutions to include in the sorting.

    Raises:
        `TypeError`: If the input is not a set of Torrent objects.

    Returns:
        `Dict[str, Torrent]`: A dictionary of Torrent objects sorted by resolution and rank in descending order,
        with the torrent's infohash as the key.
    """

    if not isinstance(torrents, set) or not all(isinstance(t, Torrent) for t in torrents):
        raise TypeError("The input must be a set of Torrent objects.")

    if resolutions:
        torrents = {t for t in torrents if get_resolution(t) in resolutions}

    sorted_torrents: List[Torrent] = sorted(
        torrents,
        key=lambda torrent: (get_resolution(torrent).value, torrent.rank),
        reverse=True
    )

    if bucket_limit and bucket_limit > 0:
        bucket_groups: Dict[Resolution, List[Torrent]] = {}
        for torrent in sorted_torrents:
            resolution = get_resolution(torrent)
            if resolution not in bucket_groups:
                bucket_groups[resolution] = []
            bucket_groups[resolution].append(torrent)

        result = {}
        for bucket_torrents in bucket_groups.values():
            for torrent in bucket_torrents[:bucket_limit]:
                result[torrent.infohash] = torrent
        return result

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
