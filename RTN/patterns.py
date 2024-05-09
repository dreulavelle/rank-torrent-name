"""
This module contains additional parsing patterns and utilities that are used in RTN.

Functions:
- `compile_patterns`: Compile a list of patterns and return them as a list of regex.Pattern objects.
- `check_pattern`: Check if a pattern is found in the input string.
- `check_hdr_dolby_video`: Check if the title contains HDR/Dolby video patterns.
- `extract_episodes`: Extract episode numbers from the title.
- `parse_extras`: Parse the input string to extract additional information relevant to RTN processing.

Arguments:
- `patterns` (list[regex.Pattern]): A list of compiled regex patterns to check.
- `raw_title` (str): The raw title string to check.

For more information on each function, refer to the respective docstrings.
"""

from typing import Any, Dict, List

import regex
from PTT import Parser, add_defaults


def compile_patterns(patterns):
    """Compile a list of patterns and return them as a list of regex.Pattern objects."""
    return [regex.compile(pattern, regex.IGNORECASE) for pattern in patterns]

# Pattern for identifying unwanted quality. This will set `data.fetch`.
IS_TRASH_COMPILED = compile_patterns(
    [
        r"\b(?:H[DQ][ .-]*)?CAM(?:H[DQ])?(?:[ .-]*Rip)?\b",
        r"\b(?:H[DQ][ .-]*)?S[ .-]*print\b",
        r"\b(?:HD[ .-]*)?T(?:ELE)?S(?:YNC)?(?:Rip)?\b",
        r"\b(?:HD[ .-]*)?T(?:ELE)?C(?:INE)?(?:Rip)?\b",
        r"\bP(?:re)?DVD(?:Rip)?\b",
        r"\b(?:DVD?|BD|BR)?[ .-]*Scr(?:eener)?\b",
        r"\bVHS\b",
        r"\bHD[ .-]*TV(?:Rip)\b",
        r"\bDVB[ .-]*(?:Rip)?\b",
        r"\bSAT[ .-]*Rips?\b",
        r"\bTVRips?\b",
        r"\bR5|R6\b",
        r"\b(DivX|XviD)\b",
        r"\b(?:Deleted[ .-]*)?Scene(?:s)?\b",
        r"\bTrailers?\b",
        r"\b((Half.)?SBS|3D)\b",
        r"\bWEB[ .-]?DL[ .-]?Rip\b",
        r"\b(iso|rar|mp3|ogg|txt|nfo|ts|m2ts)$\b", # Common Non video extensions.
        r"\bLeaked\b", # Known cam leaks. Tested against 10k+ titles. Safe.
    ]
)

# Pattern for checking multi-audio in a torrent's title.
MULTI_AUDIO_COMPILED = compile_patterns(
    [
        r"\bmulti(?:ple)?[ .-]*(?:lang(?:uages?)?|audio|VF2)?\b",
        r"\btri(?:ple)?[ .-]*(?:audio|dub\w*)\b",
        r"\bdual[ .-]*(?:au?$|[aá]udio|line)\b",
        r"\b(?:audio|dub(?:bed)?)[ .-]*dual\b",
        r"\b(?:DUBBED|dublado|dubbing|DUBS?)\b",
    ]
)

# Pattern for checking multi-subtitle in a torrent's title.
MULTI_SUBTITLE_COMPILED = compile_patterns(
    [
        r"\bmulti(?:ple)?[ .-]*(?:lang(?:uages?)?)?\b",
        r"\bdual\b(?![ .-]*sub)",
        r"\bengl?(?:sub[A-Z]*)?\b",
        r"\beng?sub[A-Z]*\b",
    ]
)

# Pattern for checking HDR/Dolby video in a torrent's title.
HDR_DOLBY_VIDEO_COMPILED = [
    (regex.compile(pattern, regex.IGNORECASE), value)
    for pattern, value in [
        (r"\bDV\b|dolby.?vision|\bDoVi\b", "DV"),
        (r"HDR10(?:\+|plus)", "HDR10+"),
        (r"\bHDR(?:10)?\b", "HDR"),
    ]
]

# Pattern for identifying a complete series.
COMPLETE_SERIES_COMPILED = compile_patterns(
    [
        r"(?:\bthe\W)?(?:\bcomplete|collection|dvd)?\b[ .]?\bbox[ .-]?set\b",
        r"(?:\bthe\W)?(?:\bcomplete|collection|dvd)?\b[ .]?\bmini[ .-]?series\b",
        r"(?:\bthe\W)?(?:\bcomplete|full|all)\b.*\b(?:series|seasons|collection|episodes|set|pack|movies)\b",
        r"\b(?:series|seasons|movies?)\b.*\b(?:complete|collection)\b",
        r"(?:\bthe\W)?\bultimate\b[ .]\bcollection\b",
        r"\bcollection\b.*\b(?:set|pack|movies)\b",
        r"\bcollection\b",
        r"duology|trilogy|quadr[oi]logy|tetralogy|pentalogy|hexalogy|heptalogy|anthology|saga",
    ],
)


IS_MOVIE_COMPILED = [
    regex.compile(r"[se]\d\d", regex.IGNORECASE),
    regex.compile(r"\b(tv|complete)\b", regex.IGNORECASE),
    regex.compile(r"\b(saisons?|stages?|seasons?).?\d", regex.IGNORECASE),
    regex.compile(r"[a-z]\s?\-\s?\d{2,4}\b", regex.IGNORECASE),
    regex.compile(r"\d{2,4}\s?\-\s?\d{2,4}\b", regex.IGNORECASE),
]


def check_video_extension(raw_title: str) -> bool:
    """Check if the title contains a video extension."""
    return bool(regex.search(r"\.(mkv|mp4|avi)$", raw_title, regex.IGNORECASE))


def check_pattern(patterns: list[regex.Pattern], raw_title: str) -> bool:
    """Check if a pattern is found in the input string."""
    return any(pattern.search(raw_title) for pattern in patterns)


def check_hdr_dolby_video(raw_title: str) -> str:
    """Returns the HDR/Dolby video type if found in the title."""
    for pattern, value in HDR_DOLBY_VIDEO_COMPILED:
        if pattern.search(raw_title):
            return value
    return ""


def check_4k_video(raw_title: str) -> bool:
    """Check if the title contains 4K or 2160p patterns."""
    return bool(regex.search(r"\b4K|2160p\b", raw_title, regex.IGNORECASE))


def extract_seasons(raw_title: str) -> List[int]:
    """
    Extract season numbers from the title or filename.
    
    Parameters:
    - `raw_title` (str): The original title of the torrent to analyze.

    Returns:
    - List[int]: A list of extracted season numbers from the title.
    """
    if not raw_title or not isinstance(raw_title, str):
        raise TypeError("The input title must be a non-empty string.")

    ptt = parsett(raw_title)
    return ptt.get("seasons", [])


def extract_episodes(raw_title: str) -> List[int]:
    """
    Extract episode numbers from the title or filename.
    
    Parameters:
    - `raw_title` (str): The original title of the torrent to analyze.

    Returns:
    - List[int]: A list of extracted episode numbers from the title.
    """
    if not raw_title or not isinstance(raw_title, str):
        raise TypeError("The input title must be a non-empty string.")

    ptt = parsett(raw_title)
    return ptt.get("episodes", [])


def parsett(raw_title: str) -> Dict[str, Any]:
    """
    Parses the input string to extract additional information relevant to RTN processing.

    Parameters:
    - raw_title (str): The original title of the torrent to analyze.

    Returns:
    - Dict[str, Any]: A dictionary containing extracted information from the torrent title.
    """
    if not raw_title or not isinstance(raw_title, str):
        raise TypeError("The input title must be a non-empty string.")

    p = Parser()
    add_defaults(p)
    return p.parse(raw_title)


def parse_extras(raw_title: str) -> Dict[str, Any]:
    """
    Parses the input string to extract additional information relevant to RTN processing.

    Parameters:
    - raw_title (str): The original title of the torrent to analyze.

    Returns:
    - Dict[str, Any]: A dictionary containing extracted information from the torrent title.
    """
    if not raw_title or not isinstance(raw_title, str):
        raise TypeError("The input title must be a non-empty string.")

    ptt = parsett(raw_title)

    return {
        "is_multi_audio": check_pattern(MULTI_AUDIO_COMPILED, raw_title),
        "is_multi_subtitle": check_pattern(MULTI_SUBTITLE_COMPILED, raw_title),
        "is_complete": check_pattern(COMPLETE_SERIES_COMPILED, raw_title),
        "is_4k": check_4k_video(raw_title),
        "hdr": check_hdr_dolby_video(raw_title) or "",
        # "episode": extract_episodes(raw_title),
        "title": ptt.get("title", ""),
        "episode_code": ptt.get("episode_code", ""),
        "episode": ptt.get("episodes", []),
        "season": ptt.get("seasons", []),
        "languages": ptt.get("language", []),
        "date": ptt.get("date", None),
        "group": ptt.get("group", ""),
        "volumes": ptt.get("volumes", []),
        "container": ptt.get("container", ""),
        "filetype": ptt.get("filetype", ""),
        "codec": ptt.get("codec", ""),
        "source": ptt.get("source", ""),
        "extended": ptt.get("extended", ""),
        "convert": ptt.get("convert", ""),
        "remastered": ptt.get("remastered", "")
    }
