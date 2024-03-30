import regex

from .models import ParsedData, SettingsModel
from .patterns import IS_TRASH_COMPILED


def check_trash(raw_title: str) -> bool:
    """Check if the title contains any trash patterns."""
    if not raw_title or not isinstance(raw_title, str):
        raise TypeError("The input title must be a non-empty string.")
    # True if we find any of the trash patterns in the title.
    # You can safely remove any title from being scraped if this returns True!
    return any(pattern.search(raw_title) for pattern in IS_TRASH_COMPILED)


def check_fetch(data: ParsedData, settings: SettingsModel) -> bool:
    """Check user settings and unwanted quality to determine if torrent should be fetched."""
    if check_trash(data.raw_title):
        return False
    if check_required(data, settings):
        return True
    if check_exclude(data, settings):
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
    if not data.quality and not data.remux:
        return True

    if data.remux:
        return settings.custom_ranks["remux"].fetch

    match data.quality[0]:
        case "WEB-DL":
            return settings.custom_ranks["webdl"].fetch
        case _:
            return True


def fetch_resolution(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the resolution is fetchable based on user settings."""
    if not data.resolution:
        return True

    resolution = data.resolution[0]
    match resolution:
        case "4K":
            return settings.custom_ranks["uhd"].fetch
        case "2160p":
            return settings.custom_ranks["uhd"].fetch
        case "1440p":
            return settings.custom_ranks["uhd"].fetch
        case "1080p":
            return settings.custom_ranks["fhd"].fetch
        case "720p":
            return settings.custom_ranks["hd"].fetch
        case "576p" | "480p":
            return settings.custom_ranks["sd"].fetch
        case _:
            return True


def fetch_codec(data: ParsedData, settings: SettingsModel) -> bool:

    if not data.codec:
        return True
    
    match data.codec[0]:
        case "AV1":
            return settings.custom_ranks["av1"].fetch
        case _:
            return True


def fetch_audio(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the audio is fetchable based on user settings."""
    if not data.audio:
        return True

    # Remove unwanted audio concatenations.
    audio: str = data.audio[0]
    audio = regex.sub(r"7.1|5.1|Dual|Mono|Original|LiNE", "", audio).strip()
    match audio:
        case "Dolby TrueHD":
            return settings.custom_ranks["truehd"].fetch
        case "Dolby Atmos":
            return settings.custom_ranks["atmos"].fetch
        case "Dolby Digital":
            return settings.custom_ranks["ac3"].fetch
        case "Dolby Digital EX":
            return settings.custom_ranks["dts_x"].fetch
        case "Dolby Digital Plus":
            return settings.custom_ranks["ddplus"].fetch
        case "DTS-HD MA":
            return settings.custom_ranks["dts_hd_ma"].fetch
        case "DTS":
            return settings.custom_ranks["dts_hd"].fetch
        case "AAC":
            return settings.custom_ranks["aac"].fetch
        case _:
            # If the audio format isn't specifically mentioned, default to True, 
            # meaning it's considered fetchable unless explicitly excluded.
            return True


def fetch_other(data: ParsedData, settings: SettingsModel) -> bool:
    """Check if the other data is fetchable based on user settings."""
    if data.proper:
        return settings.custom_ranks["proper"].fetch
    if data.repack:
        return settings.custom_ranks["repack"].fetch
    return True