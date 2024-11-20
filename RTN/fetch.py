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


def check_fetch(data: ParsedData, settings: SettingsModel, speed_mode: bool = True) -> tuple[bool, set]:
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

    failed_keys = set()

    if speed_mode:
        if trash_handler(data, settings, failed_keys):
            return False, failed_keys
        if adult_handler(data, settings, failed_keys):
            return False, failed_keys
        if check_required(data, settings):
            return True, failed_keys
        if check_exclude(data, settings, failed_keys):
            return False, failed_keys
        if language_handler(data, settings, failed_keys):
            return False, failed_keys
        if fetch_resolution(data, settings, failed_keys):
            return False, failed_keys
        if fetch_quality(data, settings, failed_keys):
            return False, failed_keys
        if fetch_audio(data, settings, failed_keys):
            return False, failed_keys
        if fetch_hdr(data, settings, failed_keys):
            return False, failed_keys
        if fetch_codec(data, settings, failed_keys):
            return False, failed_keys
        if fetch_other(data, settings, failed_keys):
            return False, failed_keys
    else:
        trash_handler(data, settings, failed_keys)
        adult_handler(data, settings, failed_keys)
        check_required(data, settings)
        check_exclude(data, settings, failed_keys)
        language_handler(data, settings, failed_keys)
        fetch_resolution(data, settings, failed_keys)
        fetch_quality(data, settings, failed_keys)
        fetch_audio(data, settings, failed_keys)
        fetch_hdr(data, settings, failed_keys)
        fetch_codec(data, settings, failed_keys)
        fetch_other(data, settings, failed_keys)

    if failed_keys:
        return False, failed_keys

    return True, failed_keys

def trash_handler(data: ParsedData, settings: SettingsModel, failed_keys: set) -> bool:
    """Check if the title is trash based on user settings."""
    if settings.options["remove_all_trash"]:
        if data.quality in ["CAM", "PDTV", "R5", "SCR", "TeleCine", "TeleSync"]:
            failed_keys.add("trash_quality")
            return True
        if "HQ Clean Audio" in data.audio:
            failed_keys.add("trash_audio")
            return True
        if hasattr(data, "trash") and data.trash:
            failed_keys.add("trash_flag")
            return True
    return False


def adult_handler(data: ParsedData, settings: SettingsModel, failed_keys: set) -> bool:
    """Check if the title is adult based on user settings."""
    if data.adult and settings.options.get("remove_adult_content", True):
        failed_keys.add("trash_adult")
        return True
    return False


def language_handler(data: ParsedData, settings: SettingsModel, failed_keys: set) -> bool:
    """Check if the languages are excluded based on user settings."""
    if not data.languages and settings.options.get("remove_unknown_languages", False):
        failed_keys.add("unknown_language")
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

    excluded = set(lang for lang in data.languages if lang in exclude_languages)
    if excluded:
        for lang in excluded:
            failed_keys.add(f"lang_{lang}")
        return True
    return False


def check_required(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the title meets the required patterns."""
    if settings.require and any(pattern.search(data.raw_title) for pattern in settings.require if pattern):  # type: ignore
        return True
    return False


def check_exclude(data: ParsedData, settings: SettingsModel, failed_keys: set) -> bool:
    """Check if the title contains excluded patterns."""
    if settings.exclude:
        for pattern in settings.exclude:
            if pattern and pattern.search(data.raw_title):
                failed_keys.add(f"exclude_regex '{pattern.pattern}'")
                return True
    return False


def fetch_quality(data: ParsedData, settings: SettingsModel, failed_keys: set) -> bool:
    """Check if the quality is fetchable based on user settings."""
    if not data.quality:
        return False

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
    if category and key:
        if not settings.custom_ranks[category][key].fetch:
            failed_keys.add(f"{category}_{key}")
            return True
    return False


def fetch_resolution(data: ParsedData, settings: SettingsModel, failed_keys: set) -> bool:
    """Check if the resolution is fetchable based on user settings."""
    if not data.resolution:
        if not settings.resolutions["unknown"]:
            failed_keys.add("resolution_unknown")
            return True
        return False

    res_map = {
        "2160p": "2160p", "4k": "2160p",
        "1080p": "1080p", "1440p": "1080p",
        "720p": "720p",
        "480p": "480p", "576p": "480p",
        "360p": "360p", "240p": "360p"
    }

    res_key = res_map.get(data.resolution.lower(), "unknown")
    if not settings.resolutions[res_key]:
        failed_keys.add(f"resolution")
        return True
    return False


def fetch_codec(data: ParsedData, settings: SettingsModel, failed_keys: set) -> bool:
    """Check if the codec is fetchable based on user settings."""
    if not data.codec:
        return False

    if data.codec.lower() in ["avc", "hevc", "av1", "xvid", "mpeg"]:
        if not settings.custom_ranks["quality"][data.codec.lower()].fetch:
            failed_keys.add(f"codec_{data.codec.lower()}")
            return True
    return False


def fetch_audio(data: ParsedData, settings: SettingsModel, failed_keys: set) -> bool:
    """Check if the audio is fetchable based on user settings."""
    if not data.audio:
        return False

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
        key = audio_map[audio_format]
        if not settings.custom_ranks[category][key].fetch:
            failed_keys.add(f"{category}_{key}")
            return True
    return False


def fetch_hdr(data: ParsedData, settings: SettingsModel, failed_keys: set) -> bool:
    """Check if the HDR is fetchable based on user settings."""
    if not data.hdr:
        return False

    hdr_map = {
        "DV": "dolby_vision",
        "HDR": "hdr",
        "HDR10+": "hdr10plus",
        "SDR": "sdr"
    }

    for hdr_format in data.hdr:
        if not settings.custom_ranks["hdr"][hdr_map[hdr_format]].fetch:
            failed_keys.add(f"hdr_{hdr_map[hdr_format]}")
            return True
    return False


def fetch_other(data: ParsedData, settings: SettingsModel, failed_keys: set) -> bool:
    """Check if the other data is fetchable based on user settings."""
    fetch_map = {
        "_3d": ("extras", "three_d"),
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
        "bit_depth": ("hdr", "10bit"),
        "scene": ("extras", "scene")
    }

    for attr, (category, key) in fetch_map.items():
        if getattr(data, attr) and not settings.custom_ranks[category][key].fetch:
            failed_keys.add(f"{category}_{key}")
            return True
    return False
