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

# Patterns for parsing episodes.
EPISODE_PATTERNS_COMPILED = [
    (regex.compile(r"(?:[\W\d]|^)e[ .]?[([]?(\d{1,3}(?:[ .-]*(?:[&+]|e){1,2}[ .]?\d{1,3})+)(?:\W|$)", regex.IGNORECASE), "range"),
    (regex.compile(r"(?:[\W\d]|^)ep[ .]?[([]?(\d{1,3}(?:[ .-]*(?:[&+]|ep){1,2}[ .]?\d{1,3})+)(?:\W|$)", regex.IGNORECASE), "range"),
    (regex.compile(r"(?:[\W\d]|^)\d+[xх][ .]?[([]?(\d{1,3}(?:[ .]?[xх][ .]?\d{1,3})+)(?:\W|$)", regex.IGNORECASE), "range"),
    (regex.compile(r"(?:[\W\d]|^)(?:episodes?|[Сс]ерии:?)[ .]?[([]?(\d{1,3}(?:[ .+]*[&+][ .]?\d{1,3})+)(?:\W|$)", regex.IGNORECASE), "range"),
    (regex.compile(r"[([]?(?:\D|^)(\d{1,3}[ .]?ao[ .]?\d{1,3})[)\]]?(?:\W|$)", regex.IGNORECASE), "range"),
    (regex.compile(r"(?:[\W\d]|^)(?:e|eps?|episodes?|[Сс]ерии:?|\d+[xх])[ .]*[([]?(\d{1,3}(?:-\d{1,3})+)(?:\W|$)", regex.IGNORECASE), "range"),
    (regex.compile(r"(?:\W|^)[st]\d{1,2}[. ]?[xх-]?[. ]?(?:e|x|х|ep|-|\.)[. ]?(\d{1,3})(?:[abc]|v0?[1-4]|\D|$)", regex.IGNORECASE), "array(integer)"),
    (regex.compile(r"\b[st]\d{2}(\d{2})\b", regex.IGNORECASE), "array(integer)"),
    (regex.compile(r"(?:\W|^)(\d{1,3}(?:[ .]*~[ .]*\d{1,3})+)(?:\W|$)", regex.IGNORECASE), "range"),
    (regex.compile(r"-\s(\d{1,3}[ .]*-[ .]*\d{1,3})(?!-\d)(?:\W|$)", regex.IGNORECASE), "range"),
    (regex.compile(r"s\d{1,2}\s?\((\d{1,3}[ .]*-[ .]*\d{1,3})\)", regex.IGNORECASE), "range"),
    (regex.compile(r"(?:^|\/)\d{1,2}-(\d{2})\b(?!-\d)"), "array(integer)"),
    (regex.compile(r"(?<!\d-)\b\d{1,2}-(\d{2})(?=\.\w{2,4}$)"), "array(integer)"),
    (regex.compile(r"(?<!seasons?|[Сс]езони?)\W(?:[ .([-]|^)(\d{1,3}(?:[ .]?[,&+~][ .]?\d{1,3})+)(?:[ .)\]-]|$)", regex.IGNORECASE), "range"),
    (regex.compile(r"(?<!seasons?|[Сс]езони?)\W(?:[ .([-]|^)(\d{1,3}(?:-\d{1,3})+)(?:[ .)(\]]|-\D|$)", regex.IGNORECASE), "range"),
    (regex.compile(r"\bEp(?:isode)?\W+\d{1,2}\.(\d{1,3})\b", regex.IGNORECASE), "array(integer)"),
    (regex.compile(r"(?:\b[ée]p?(?:isode)?|[Ээ]пизод|[Сс]ер(?:ии|ия|\.)?|cap(?:itulo)?|epis[oó]dio)[. ]?[-:#№]?[. ]?(\d{1,4})(?:[abc]|v0?[1-4]|\W|$)", regex.IGNORECASE), "array(integer)"),
    (regex.compile(r"\b(\d{1,3})(?:-?я)?[ ._-]*(?:ser(?:i?[iyj]a|\b)|[Сс]ер(?:ии|ия|\.)?)", regex.IGNORECASE), "array(integer)"),
    (regex.compile(r"(?:\D|^)\d{1,2}[. ]?[xх][. ]?(\d{1,2})(?:[abc]|v0?[1-4]|\D|$)"), "array(integer)"), # Fixed: Was catching `1.x265` as episode.
    (regex.compile(r"[[(]\d{1,2}\.(\d{1,3})[)\]]"), "array(integer)"),
    (regex.compile(r"\b[Ss]\d{1,2}[ .](\d{1,2})\b"), "array(integer)"),
    (regex.compile(r"-\s?\d{1,2}\.(\d{2,3})\s?-"), "array(integer)"),
    (regex.compile(r"(?<=\D|^)(\d{1,3})[. ]?(?:of|из|iz)[. ]?\d{1,3}(?=\D|$)", regex.IGNORECASE), "array(integer)"),
    (regex.compile(r"\b\d{2}[ ._-](\d{2})(?:.F)?\.\w{2,4}$"), "array(integer)"),
    (regex.compile(r"(?<!^)\[(\d{2,3})\](?!(?:\.\w{2,4})?$)"), "array(integer)"),
]


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


def range_transform(raw_title: str) -> set[int]:
    """
    Expands a range string into a list of individual episode numbers.
    Example input: '1-3', '1&2&3', '1E2E3'
    Returns: [1, 2, 3]
    """
    episodes = set()
    # Split input string on non-digit characters, filter empty strings.
    parts = [part for part in regex.split(r"\D+", raw_title) if part]
    # Convert parts to integers, ignoring non-numeric parts.
    episode_nums = [int(part) for part in parts if part.isdigit()]
    # If it's a simple range (e.g., '1-3'), expand it.
    if len(episode_nums) == 2 and episode_nums[0] < episode_nums[1]:
        episodes.update(range(episode_nums[0], episode_nums[1] + 1))
    else:
        episodes.update(episode_nums)
    return episodes


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

    episodes = set()
    for compiled_pattern, transform in EPISODE_PATTERNS_COMPILED:
        matches = compiled_pattern.findall(raw_title)
        for match in matches:
            if transform == "range":
                episodes.update(range_transform(match))
            elif transform == "array(integer)":
                normalized_match = [match] if isinstance(match, str) else match
                episodes.update(int(m) for m in normalized_match if m.isdigit())
            else:
                return []
    return sorted(episodes)


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

    return {
        "is_multi_audio": check_pattern(MULTI_AUDIO_COMPILED, raw_title),
        "is_multi_subtitle": check_pattern(MULTI_SUBTITLE_COMPILED, raw_title),
        "is_complete": check_pattern(COMPLETE_SERIES_COMPILED, raw_title),
        "is_4k": check_4k_video(raw_title),
        "hdr": check_hdr_dolby_video(raw_title) or "",
        "episode": extract_episodes(raw_title),
    }
