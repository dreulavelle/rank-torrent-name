"""
This module contains functions to check if a torrent should be fetched based on user settings.

Functions:
- `check_trash`: Check if the title contains any unwanted patterns.
- `check_fetch`: Check user settings and unwanted quality to determine if torrent should be fetched.
- `check_required`: Check if the title meets the required patterns.
- `check_exclude`: Check if the title contains excluded patterns.
- `fetch_quality`: Check if the quality is fetchable based on user settings.
- `fetch_resolution`: Check if the resolution is fetchable based on user settings.
- `fetch_codec`: Check if the codec is fetchable based on user settings.
- `fetch_audio`: Check if the audio is fetchable based on user settings.
- `fetch_other`: Check if the other data is fetchable based on user settings.

Arguments:
- `raw_title` (str): The raw title string to check.
- `data` (ParsedData): The parsed data object containing information about the torrent title.
- `settings` (SettingsModel): The user settings object containing custom ranking models.

For more information on each function, refer to the respective docstrings.

Examples:
    >>> check_trash("Some.Title.CAM.720p.WEB-DL.x264-Group")
    True
    >>> check_trash("Some.Title.720p.WEB-DL.x264-Group")
    False
    >>> check_fetch(ParsedData, SettingsModel)
    True
    >>> check_required(ParsedData, SettingsModel)
    True
    >>> check_exclude(ParsedData, SettingsModel)
    False
    >>> fetch_resolution(ParsedData, SettingsModel)
    True
    >>> fetch_quality(ParsedData, SettingsModel)
    True
    >>> fetch_audio(ParsedData, SettingsModel)
    True
    >>> fetch_codec(ParsedData, SettingsModel)
    True
    >>> fetch_other(ParsedData, SettingsModel)
    True
"""

from .models import ParsedData, SettingsModel


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

    if settings.options["remove_all_trash"]:
        if hasattr(data, "trash") and data.trash:
            return False
        if data.quality in ["CAM", "PDTV", "R5", "SCR", "TeleCine", "TeleSync"]:
            return False

    if check_required(data, settings):
        return True
    if check_exclude(data, settings):
        return False

    if not settings.options["allow_unknown_resolutions"] and data.resolution == "unknown":
        return False

    if not settings.languages["allow_unknown_languages"] and not data.languages:
        return False

    if settings.languages["required"] and not check_exclude_languages(data, settings):
        return False

    return all(
        [
            fetch_resolution(data, settings),
            fetch_quality(data, settings),
            fetch_audio(data, settings),
            fetch_codec(data, settings),
            fetch_other(data, settings),
            check_exclude_languages(data, settings),
        ]
    )


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


def check_exclude_languages(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the languages are excluded based on user settings."""
    if not data.languages:
        return True
    return not any(language in settings.languages["exclude"] for language in data.languages)


def fetch_quality(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the quality is fetchable based on user settings."""
    if not data.quality:
        return True

    quality = data.quality

    match quality:
        case "WEB":
            return settings.custom_ranks["quality"]["web"].fetch
        case "WEB-DL":
            return settings.custom_ranks["quality"]["webdl"].fetch
        case "BluRay":
            return settings.custom_ranks["quality"]["bluray"].fetch
        case "HDTV":
            return settings.custom_ranks["quality"]["hdtv"].fetch
        case "VHS":
            return settings.custom_ranks["quality"]["vhs"].fetch
        case "WEBMux":
            return settings.custom_ranks["quality"]["webmux"].fetch
        case "BluRay REMUX" | "REMUX":
            return settings.custom_ranks["quality"]["remux"].fetch
        case "WEBRip":
            return settings.custom_ranks["rips"]["webrip"].fetch
        case "WEB-DLRip":
            return settings.custom_ranks["rips"]["webdlrip"].fetch
        case "UHDRip":
            return settings.custom_ranks["rips"]["uhdrip"].fetch
        case "HDRip":
            return settings.custom_ranks["rips"]["hdrip"].fetch
        case "DVDRip":
            return settings.custom_ranks["rips"]["dvdrip"].fetch
        case "BDRip":
            return settings.custom_ranks["rips"]["bdrip"].fetch
        case "BRRip":
            return settings.custom_ranks["rips"]["brrip"].fetch
        case "VHSRip":
            return settings.custom_ranks["rips"]["vhsrip"].fetch
        case "PPVRip":
            return settings.custom_ranks["rips"]["ppvrip"].fetch
        case "SATRip":
            return settings.custom_ranks["rips"]["satrip"].fetch
        case "TeleCine":
            return settings.custom_ranks["trash"]["telecine"].fetch
        case "TeleSync":
            return settings.custom_ranks["trash"]["telesync"].fetch
        case "SCR":
            return settings.custom_ranks["trash"]["screener"].fetch
        case "R5":
            return settings.custom_ranks["trash"]["r5"].fetch
        case "CAM":
            return settings.custom_ranks["trash"]["cam"].fetch
        case "PDTV":
            return settings.custom_ranks["trash"]["pdtv"].fetch
        case _:
            return True


def fetch_resolution(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the resolution is fetchable based on user settings."""
    if not data.resolution:
        return settings.options.get("allow_unknown_resolutions", False)

    match data.resolution.lower():
        case "2160p" | "4k" | "2160i":
            return settings.custom_ranks["resolution"]["2160p"].fetch
        case "1080p" | "1080i" | "1440p":
            return settings.custom_ranks["resolution"]["1080p"].fetch
        case "720p" | "720i":
            return settings.custom_ranks["resolution"]["720p"].fetch
        case "480p" | "576p" | "480i" | "576i":
            return settings.custom_ranks["resolution"]["480p"].fetch
        case "360p" | "240p" | "360i" | "240i":
            return settings.custom_ranks["resolution"]["360p"].fetch
        case _:
            return settings.options.get("allow_unknown_resolutions", False)


def fetch_codec(data: ParsedData, settings: SettingsModel) -> bool:

    if not data.codec:
        return True

    match data.codec:
        case "avc":
            return settings.custom_ranks["quality"]["avc"].fetch
        case "hevc":
            return settings.custom_ranks["quality"]["hevc"].fetch
        case "av1":
            return settings.custom_ranks["quality"]["av1"].fetch
        case "xvid":
            return settings.custom_ranks["quality"]["xvid"].fetch
        case "mpeg":
            return settings.custom_ranks["quality"]["mpeg"].fetch
        case _:
            return True


def fetch_audio(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the audio is fetchable based on user settings."""
    if not data.audio:
        return True

    for audio_format in data.audio:
        match audio_format:
            case "AAC":
                if not settings.custom_ranks["audio"]["aac"].fetch:
                    return False
            case "AC3":
                if not settings.custom_ranks["audio"]["ac3"].fetch:
                    return False
            case "Atmos":
                if not settings.custom_ranks["audio"]["atmos"].fetch:
                    return False
            case "Dolby Digital":
                if not settings.custom_ranks["audio"]["dolby_digital"].fetch:
                    return False
            case "Dolby Digital Plus":
                if not settings.custom_ranks["audio"]["dolby_digital_plus"].fetch:
                    return False
            case "DTS Lossy":
                if not settings.custom_ranks["audio"]["dts_lossy"].fetch:
                    return False
            case "DTS Lossless":
                if not settings.custom_ranks["audio"]["dts_lossless"].fetch:
                    return False
            case "EAC3":
                if not settings.custom_ranks["audio"]["eac3"].fetch:
                    return False
            case "FLAC":
                if not settings.custom_ranks["audio"]["flac"].fetch:
                    return False
            case "MP3":
                if not settings.custom_ranks["audio"]["mp3"].fetch:
                    return False
            case "TrueHD":
                if not settings.custom_ranks["audio"]["truehd"].fetch:
                    return False
            case "HQ Clean Audio":
                if not settings.custom_ranks["trash"]["clean_audio"].fetch:
                    return False
    return True


def fetch_other(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the other data is fetchable based on user settings."""
    if data._3d:
        return settings.custom_ranks["extras"]["3d"].fetch
    if data.converted:
        return settings.custom_ranks["extras"]["converted"].fetch
    if data.documentary:
        return settings.custom_ranks["extras"]["documentary"].fetch
    if data.dubbed:
        return settings.custom_ranks["extras"]["dubbed"].fetch
    if data.edition:
        return settings.custom_ranks["extras"]["edition"].fetch
    if data.hardcoded:
        return settings.custom_ranks["extras"]["hardcoded"].fetch
    if data.network:
        return settings.custom_ranks["extras"]["network"].fetch
    if data.proper:
        return settings.custom_ranks["extras"]["proper"].fetch
    if data.repack:
        return settings.custom_ranks["extras"]["repack"].fetch
    if data.retail:
        return settings.custom_ranks["extras"]["retail"].fetch
    if data.subbed:
        return settings.custom_ranks["extras"]["subbed"].fetch
    if data.upscaled:
        return settings.custom_ranks["extras"]["upscaled"].fetch
    return True
