"""
This module contains functions to determine if a torrent should be fetched based on user settings.

Functions:
- `check_fetch`: Evaluates user settings and unwanted quality to decide if a torrent should be fetched.
- `check_trash`: Identifies if the title contains any unwanted patterns.
- `trash_handler`: Checks if the title is trash based on user settings, return True if trash is detected.
- `language_handler`: Checks if the languages are excluded based on user settings.

Parameters:
- `raw_title` (str): The raw title string to evaluate.
- `data` (ParsedData): The parsed data object containing information about the torrent title.
- `settings` (SettingsModel): The user settings object containing custom ranking models.

For more information on each function, refer to the respective docstrings.
"""

from .models import ParsedData, SettingsModel

ANIME = {"ja", "zh", "ko"}
NON_ANIME = {
    "de", "es", "hi", "ta", "ru", "ua", "th", "it",
    "ar", "pt", "fr", "pa", "mr", "gu", "te", "kn",
    "ml", "vi", "id", "tr", "he", "fa", "el", "lt",
    "lv", "et", "pl", "cs", "sk", "hu", "ro", "bg",
    "sr", "hr", "sl", "nl", "da", "fi", "sv", "no",
    "ms"
}

COMMON = {"de", "es", "hi", "ta", "ru", "ua", "th", "it", "zh", "ar", "fr"}
ALL = ANIME | NON_ANIME


def check_fetch(data: ParsedData, settings: SettingsModel) -> bool:
    """
    Check user settings and unwanted quality to determine if torrent should be fetched.
    
    Parameters:
        `data` (ParsedData): The parsed data object containing information about the torrent title.
        `settings` (SettingsModel): The user settings object containing custom ranking models.
    
    Returns:
        bool: True if the torrent should be fetched, otherwise False.
    
    Raises:
        TypeError: If the parsed data is not a ParsedData object.
        TypeError: If the settings is not a SettingsModel object.
    """
    if not isinstance(data, ParsedData):
        raise TypeError("Parsed data must be an instance of ParsedData.")
    if not isinstance(settings, SettingsModel):
        raise TypeError("Settings must be an instance of SettingsModel.")

    if trash_handler(data, settings):
        return False
    if check_required(data, settings):
        return True
    if check_exclude(data, settings):
        return False
    if language_handler(data, settings):
        return False

    return all(
        [
            fetch_resolution(data, settings),
            fetch_quality(data, settings),
            fetch_audio(data, settings),
            fetch_codec(data, settings),
            fetch_other(data, settings),
        ]
    )


def trash_handler(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the title is trash based on user settings, return True if trash is detected."""
    if settings.options["remove_all_trash"]:
        if data.quality in ["CAM", "PDTV", "R5", "SCR", "TeleCine", "TeleSync"]:
            return True
        if "HQ Clean Audio" in data.audio:
            return True
        if hasattr(data, "trash") and data.trash:
            return True
    return False


def language_handler(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the languages are excluded based on user settings."""
    if not data.languages and settings.options.get("remove_unknown_languages", False):
        return True

    exclude_languages = set(settings.languages.get("exclude", []))
    if "anime" in exclude_languages:
        exclude_languages.update(ANIME)
    if "non_anime" in exclude_languages:
        exclude_languages.update(NON_ANIME)
    if "common" in exclude_languages:
        exclude_languages.update(COMMON)
    if "all" in exclude_languages:
        exclude_languages.update(ALL)

    if "en" in data.languages and settings.options.get("allow_english_in_languages", False):
        return False

    return any(language in exclude_languages for language in data.languages)


def check_required(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the title meets the required patterns."""
    if settings.require and any(pattern.search(data.raw_title) for pattern in settings.require if pattern):  # type: ignore
        return True
    return False


def check_exclude(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the title contains excluded patterns."""
    if settings.exclude and any(pattern.search(data.raw_title) for pattern in settings.exclude if pattern):  # type: ignore
        return True
    return False


def fetch_quality(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the quality is fetchable based on user settings."""
    if not data.quality:
        return True

    quality_map = {
        # parse result, (settings location, settings key)
        "WEB": ("quality", "web"),
        "WEB-DL": ("quality", "webdl"),
        "BluRay": ("quality", "bluray"),
        "HDTV": ("quality", "hdtv"),
        "VHS": ("quality", "vhs"),
        "WEBMux": ("quality", "webmux"),
        "BluRay REMUX": ("quality", "remux"),
        "REMUX": ("quality", "remux"),
        "WEBRip": ("rips", "webrip"),
        "WEB-DLRip": ("rips", "webdlrip"),
        "UHDRip": ("rips", "uhdrip"),
        "HDRip": ("rips", "hdrip"),
        "DVDRip": ("rips", "dvdrip"),
        "BDRip": ("rips", "bdrip"),
        "BRRip": ("rips", "brrip"),
        "VHSRip": ("rips", "vhsrip"),
        "PPVRip": ("rips", "ppvrip"),
        "SATRip": ("rips", "satrip"),
        "TeleCine": ("trash", "telecine"),
        "TeleSync": ("trash", "telesync"),
        "SCR": ("trash", "screener"),
        "R5": ("trash", "r5"),
        "CAM": ("trash", "cam"),
        "PDTV": ("trash", "pdtv")
    }

    category, key = quality_map.get(data.quality, (None, None))
    return settings.custom_ranks[category][key].fetch if category and key else True


def fetch_resolution(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the resolution is fetchable based on user settings."""
    if not data.resolution:
        return settings.resolutions["unknown"]

    match data.resolution.lower():
        case "2160p" | "4k":
            return settings.resolutions["2160p"]
        case "1080p" | "1440p":
            return settings.resolutions["1080p"]
        case "720p":
            return settings.resolutions["720p"]
        case "480p" | "576p":
            return settings.resolutions["480p"]
        case "360p" | "240p":
            return settings.resolutions["360p"]
        case _:
            return settings.resolutions["unknown"]


def fetch_codec(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the codec is fetchable based on user settings."""
    if not data.codec:
        return True

    codec_map = {
        "avc": settings.custom_ranks["quality"]["avc"].fetch,
        "hevc": settings.custom_ranks["quality"]["hevc"].fetch,
        "av1": settings.custom_ranks["quality"]["av1"].fetch,
        "xvid": settings.custom_ranks["quality"]["xvid"].fetch,
        "mpeg": settings.custom_ranks["quality"]["mpeg"].fetch,
    }

    return codec_map.get(data.codec, True)


def fetch_audio(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the audio is fetchable based on user settings."""
    if not data.audio:
        return True

    audio_map = {
        "AAC": "aac",
        "AC3": "ac3",
        "Atmos": "atmos",
        "Dolby Digital": "dolby_digital",
        "Dolby Digital Plus": "dolby_digital_plus",
        "DTS Lossy": "dts_lossy",
        "DTS Lossless": "dts_lossless",
        "EAC3": "eac3",
        "FLAC": "flac",
        "MP3": "mp3",
        "TrueHD": "truehd",
        "HQ Clean Audio": "clean_audio"
    }

    for audio_format in data.audio:
        category = "trash" if audio_format == "HQ Clean Audio" else "audio"
        if not settings.custom_ranks[category][audio_map[audio_format]].fetch:
            return False
    return True


def fetch_other(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the other data is fetchable based on user settings."""
    fetch_map = {
        "_3d": ("extras", "3d"),
        "converted": ("extras", "converted"),
        "documentary": ("extras", "documentary"),
        "dubbed": ("extras", "dubbed"),
        "edition": ("extras", "edition"),
        "hardcoded": ("extras", "hardcoded"),
        "network": ("extras", "network"),
        "proper": ("extras", "proper"),
        "repack": ("extras", "repack"),
        "retail": ("extras", "retail"),
        "subbed": ("extras", "subbed"),
        "upscaled": ("extras", "upscaled"),
        "site": ("extras", "site"),
        "size": ("trash", "size"),
        "bit_depth": ("hdr", "10bit")
    }

    for attr, (category, key) in fetch_map.items():
        if getattr(data, attr) and not settings.custom_ranks[category][key].fetch:
            return False
    return True
