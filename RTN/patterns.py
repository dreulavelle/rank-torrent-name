"""
This module contains additional parsing patterns and utilities that are used in RTN.

Functions:
- `normalize_title`: Normalize the title string to remove unwanted characters and patterns.
- `check_video_extension`: Check if the title contains a video extension.
- `check_pattern`: Check if a pattern is found in the input string.

Arguments:
- `patterns` (list[regex.Pattern]): A list of compiled regex patterns to check.
- `raw_title` (str): The raw title string to check.

For more information on each function, refer to the respective docstrings.
"""

import regex


# Translation table for normalizing unicode characters
translationTable: dict[str, str] = {
    "ā": "a", "ă": "a", "ą": "a", "ć": "c", "č": "c", "ç": "c",
    "ĉ": "c", "ċ": "c", "ď": "d", "đ": "d", "è": "e", "é": "e",
    "ê": "e", "ë": "e", "ē": "e", "ĕ": "e", "ę": "e", "ě": "e",
    "ĝ": "g", "ğ": "g", "ġ": "g", "ģ": "g", "ĥ": "h", "î": "i",
    "ï": "i", "ì": "i", "í": "i", "ī": "i", "ĩ": "i", "ĭ": "i",
    "ı": "i", "ĵ": "j", "ķ": "k", "ĺ": "l", "ļ": "l", "ł": "l",
    "ń": "n", "ň": "n", "ñ": "n", "ņ": "n", "ŉ": "n", "ó": "o",
    "ô": "o", "õ": "o", "ö": "o", "ø": "o", "ō": "o", "ő": "o",
    "œ": "oe", "ŕ": "r", "ř": "r", "ŗ": "r", "š": "s", "ş": "s",
    "ś": "s", "ș": "s", "ß": "ss", "ť": "t", "ţ": "t", "ū": "u",
    "ŭ": "u", "ũ": "u", "û": "u", "ü": "u", "ù": "u", "ú": "u",
    "ų": "u", "ű": "u", "ŵ": "w", "ý": "y", "ÿ": "y", "ŷ": "y",
    "ž": "z", "ż": "z", "ź": "z", "æ": "ae", "ǎ": "a", "ǧ": "g",
    "ə": "e", "ƒ": "f", "ǐ": "i", "ǒ": "o", "ǔ": "u", "ǚ": "u",
    "ǜ": "u", "ǹ": "n", "ǻ": "a", "ǽ": "ae", "ǿ": "o", "!": None,
    "?": None, ",": None, ".": None, ":": None, ";": None,
}


def normalize_title(raw_title: str, lower: bool = True) -> str:
    """Normalize the title to remove special characters and accents."""
    import unicodedata
    translation_table = str.maketrans(translationTable)
    lowered = raw_title.lower() if lower else raw_title
    # Normalize unicode characters to their closest ASCII equivalent
    normalized = unicodedata.normalize('NFKD', lowered)
    # Encode to ASCII bytes, ignoring non-ASCII characters, then decode back to string
    ascii_title = normalized.encode('ascii', 'ignore').decode('ascii')
    # Apply specific translations
    return ascii_title.translate(translation_table)


def check_video_extension(raw_title: str) -> bool:
    """Check if the title contains a video extension."""
    return bool(regex.search(r"\.(mkv|mp4|avi)$", raw_title, regex.IGNORECASE))


def check_pattern(patterns: list[regex.Pattern], raw_title: str) -> bool:
    """Check if a pattern is found in the input string."""
    return any(pattern.search(raw_title) for pattern in patterns)
