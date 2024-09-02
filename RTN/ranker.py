"""
This module contains functions to rank parsed data based on user settings and custom ranking models.

Functions:
- `get_rank`: Calculate the ranking of the given parsed data.
- `calculate_preferred`: Calculate the preferred ranking of a given parsed data.
- `calculate_quality_rank`: Calculate the quality ranking of the given parsed data.
- `calculate_codec_rank`: Calculate the codec ranking of the given parsed data.
- `calculate_audio_rank`: Calculate the audio ranking of the given parsed data.
- `calculate_extra_ranks`: Calculate all the other rankings of the given parsed data.

Arguments:
- `data` (ParsedData): The parsed data object containing information about the torrent title.
- `settings` (SettingsModel): The user settings object containing custom ranking models.
- `rank_model` (BaseRankingModel): The base ranking model used for calculating the ranking.

For more information on each function, refer to the respective docstrings.

Examples:
    >>> get_rank(ParsedData, SettingsModel, BaseRankingModel)
    250
"""

import regex

from .models import BaseRankingModel, ParsedData, SettingsModel


def get_rank(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """
    Calculate the ranking of the given parsed data.

    Parameters:
        `data` (ParsedData): The parsed data object containing information about the torrent title.
        `settings` (SettingsModel): The user settings object containing custom ranking models.
        `rank_model` (BaseRankingModel): The base ranking model used for calculating the ranking.

    Returns:
        int: The calculated ranking value for the parsed data.

    Raises:
        ValueError: If the parsed data is empty.
        TypeError: If the parsed data is not a ParsedData object.
    """
    if not isinstance(data, ParsedData):
        raise TypeError("Parsed data must be an instance of ParsedData.")
    if not data.raw_title:
        raise ValueError("Parsed data cannot be empty.")

    rank: int = 0
    rank += calculate_quality_rank(data, settings, rank_model)
    rank += calculate_hdr_rank(data, settings, rank_model)
    rank += calculate_channels_rank(data, settings, rank_model)
    rank += calculate_audio_rank(data, settings, rank_model)
    rank += calculate_codec_rank(data, settings, rank_model)
    rank += calculate_extra_ranks(data, settings, rank_model)
    rank += calculate_preferred(data, settings)
    rank += calculate_preferred_langs(data, settings)
    return rank


def calculate_preferred(data: ParsedData, settings: SettingsModel) -> int:
    """Calculate the preferred ranking of a given parsed data."""
    if not settings.preferred or all(pattern is None for pattern in settings.preferred):
        return 0
    return 10000 if any(regex.search(pattern, data.raw_title) for pattern in settings.preferred if pattern) else 0


def calculate_preferred_langs(data: ParsedData, settings: SettingsModel) -> int:
    """Calculate the preferred languages ranking of a given parsed data."""
    if not settings.languages["preferred"]:
        return 0
    return 10000 if any(lang in data.languages for lang in settings.languages["preferred"]) else 0


def calculate_quality_rank(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate the quality ranking of the given parsed data."""
    if not data.quality:
        return 0

    quality = data.quality
    match quality:
        # Quality
        case "WEB":
            return rank_model.web if not settings.custom_ranks["quality"]["web"].use_custom_rank else settings.custom_ranks["quality"]["web"].rank
        case "WEB-DL":
            return rank_model.webdl if not settings.custom_ranks["quality"]["webdl"].use_custom_rank else settings.custom_ranks["quality"]["webdl"].rank
        case "BluRay":
            return rank_model.bluray if not settings.custom_ranks["quality"]["bluray"].use_custom_rank else settings.custom_ranks["quality"]["bluray"].rank
        case "HDTV":
            return rank_model.hdtv if not settings.custom_ranks["quality"]["hdtv"].use_custom_rank else settings.custom_ranks["quality"]["hdtv"].rank
        case "VHS":
            return rank_model.vhs if not settings.custom_ranks["quality"]["vhs"].use_custom_rank else settings.custom_ranks["quality"]["vhs"].rank
        case "WEBMux":
            return rank_model.webmux if not settings.custom_ranks["quality"]["webmux"].use_custom_rank else settings.custom_ranks["quality"]["webmux"].rank
        case "BluRay REMUX" | "REMUX":
            return rank_model.remux if not settings.custom_ranks["quality"]["remux"].use_custom_rank else settings.custom_ranks["quality"]["remux"].rank

        # Rips
        case "WEBRip":
            return rank_model.webrip if not settings.custom_ranks["rips"]["webrip"].use_custom_rank else settings.custom_ranks["rips"]["webrip"].rank
        case "WEB-DLRip":
            return rank_model.webdlrip if not settings.custom_ranks["rips"]["webdlrip"].use_custom_rank else settings.custom_ranks["rips"]["webdlrip"].rank
        case "UHDRip":
            return rank_model.uhdrip if not settings.custom_ranks["rips"]["uhdrip"].use_custom_rank else settings.custom_ranks["rips"]["uhdrip"].rank
        case "HDRip":
            return rank_model.hdrip if not settings.custom_ranks["rips"]["hdrip"].use_custom_rank else settings.custom_ranks["rips"]["hdrip"].rank
        case "DVDRip":
            return rank_model.dvdrip if not settings.custom_ranks["rips"]["dvdrip"].use_custom_rank else settings.custom_ranks["rips"]["dvdrip"].rank
        case "BDRip":
            return rank_model.bdrip if not settings.custom_ranks["rips"]["bdrip"].use_custom_rank else settings.custom_ranks["rips"]["bdrip"].rank
        case "BRRip":
            return rank_model.brrip if not settings.custom_ranks["rips"]["brrip"].use_custom_rank else settings.custom_ranks["rips"]["brrip"].rank
        case "VHSRip":
            return rank_model.vhsrip if not settings.custom_ranks["rips"]["vhsrip"].use_custom_rank else settings.custom_ranks["rips"]["vhsrip"].rank
        case "PPVRip":
            return rank_model.ppvrip if not settings.custom_ranks["rips"]["ppvrip"].use_custom_rank else settings.custom_ranks["rips"]["ppvrip"].rank
        case "SATRip":
            return rank_model.satrip if not settings.custom_ranks["rips"]["satrip"].use_custom_rank else settings.custom_ranks["rips"]["satrip"].rank
        case "TVRip":
            return rank_model.tvrip if not settings.custom_ranks["rips"]["tvrip"].use_custom_rank else settings.custom_ranks["rips"]["tvrip"].rank

        # Trash
        case "TeleCine":
            return rank_model.telecine if not settings.custom_ranks["trash"]["telecine"].use_custom_rank else settings.custom_ranks["trash"]["telecine"].rank
        case "TeleSync":
            return rank_model.telesync if not settings.custom_ranks["trash"]["telesync"].use_custom_rank else settings.custom_ranks["trash"]["telesync"].rank
        case "SCR":
            return rank_model.screener if not settings.custom_ranks["trash"]["screener"].use_custom_rank else settings.custom_ranks["trash"]["screener"].rank
        case "R5":
            return rank_model.r5 if not settings.custom_ranks["trash"]["r5"].use_custom_rank else settings.custom_ranks["trash"]["r5"].rank
        case "CAM":
            return rank_model.cam if not settings.custom_ranks["trash"]["cam"].use_custom_rank else settings.custom_ranks["trash"]["cam"].rank
        case "PDTV":
            return rank_model.pdtv if not settings.custom_ranks["trash"]["pdtv"].use_custom_rank else settings.custom_ranks["trash"]["pdtv"].rank
        case _:
            return 0


def calculate_codec_rank(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate the codec ranking of the given parsed data."""
    if not data.codec:
        return 0

    codec = data.codec.lower()
    match codec:
        case "avc":
            return rank_model.avc if not settings.custom_ranks["quality"]["avc"].use_custom_rank else settings.custom_ranks["quality"]["avc"].rank
        case "hevc":
            return rank_model.hevc if not settings.custom_ranks["quality"]["hevc"].use_custom_rank else settings.custom_ranks["quality"]["hevc"].rank
        case "xvid":
            return rank_model.xvid if not settings.custom_ranks["quality"]["xvid"].use_custom_rank else settings.custom_ranks["quality"]["xvid"].rank
        case "av1":
            return rank_model.av1 if not settings.custom_ranks["quality"]["av1"].use_custom_rank else settings.custom_ranks["quality"]["av1"].rank
        case "mpeg":
            return rank_model.mpeg if not settings.custom_ranks["quality"]["mpeg"].use_custom_rank else settings.custom_ranks["quality"]["mpeg"].rank
        case _:
            return 0


def calculate_hdr_rank(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate the codec ranking of the given parsed data."""
    if not data.hdr:
        return 0

    total_rank = 0
    for hdr in data.hdr:
        match hdr:
            case "DV":
                total_rank += rank_model.dolby_vision if not settings.custom_ranks["hdr"]["dolby_vision"].use_custom_rank else settings.custom_ranks["hdr"]["dolby_vision"].rank
            case "HDR":
                total_rank += rank_model.hdr if not settings.custom_ranks["hdr"]["hdr"].use_custom_rank else settings.custom_ranks["hdr"]["hdr"].rank
            case "HDR10+":
                total_rank += rank_model.hdr10plus if not settings.custom_ranks["hdr"]["hdr10plus"].use_custom_rank else settings.custom_ranks["hdr"]["hdr10plus"].rank
            case "SDR":
                total_rank += rank_model.sdr if not settings.custom_ranks["hdr"]["sdr"].use_custom_rank else settings.custom_ranks["hdr"]["sdr"].rank
            case _:
                total_rank += 0

    if data.bit_depth:
        total_rank += rank_model.bit_10 if not settings.custom_ranks["hdr"]["10bit"].use_custom_rank else settings.custom_ranks["hdr"]["10bit"].rank

    return total_rank


def calculate_audio_rank(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate the audio ranking of the given parsed data."""
    if not data.audio:
        return 0

    total_rank = 0

    for audio_format in data.audio:
        match audio_format:
            case "AAC":
                total_rank += rank_model.aac if not settings.custom_ranks["audio"]["aac"].use_custom_rank else settings.custom_ranks["audio"]["aac"].rank
            case "AC3":
                total_rank += rank_model.ac3 if not settings.custom_ranks["audio"]["ac3"].use_custom_rank else settings.custom_ranks["audio"]["ac3"].rank
            case "Atmos":
                total_rank += rank_model.atmos if not settings.custom_ranks["audio"]["atmos"].use_custom_rank else settings.custom_ranks["audio"]["atmos"].rank
            case "Dolby Digital":
                total_rank += rank_model.dolby_digital if not settings.custom_ranks["audio"]["dolby_digital"].use_custom_rank else settings.custom_ranks["audio"]["dolby_digital"].rank
            case "Dolby Digital Plus":
                total_rank += rank_model.dolby_digital_plus if not settings.custom_ranks["audio"]["dolby_digital_plus"].use_custom_rank else settings.custom_ranks["audio"]["dolby_digital_plus"].rank
            case "DTS Lossy":
                total_rank += rank_model.dts_lossy if not settings.custom_ranks["audio"]["dts_lossy"].use_custom_rank else settings.custom_ranks["audio"]["dts_lossy"].rank
            case "DTS Lossless":
                total_rank += rank_model.dts_lossless if not settings.custom_ranks["audio"]["dts_lossless"].use_custom_rank else settings.custom_ranks["audio"]["dts_lossless"].rank
            case "EAC3":
                total_rank += rank_model.eac3 if not settings.custom_ranks["audio"]["eac3"].use_custom_rank else settings.custom_ranks["audio"]["eac3"].rank
            case "FLAC":
                total_rank += rank_model.flac if not settings.custom_ranks["audio"]["flac"].use_custom_rank else settings.custom_ranks["audio"]["flac"].rank
            case "MP3":
                total_rank += rank_model.mp3 if not settings.custom_ranks["audio"]["mp3"].use_custom_rank else settings.custom_ranks["audio"]["mp3"].rank
            case "TrueHD":
                total_rank += rank_model.truehd if not settings.custom_ranks["audio"]["truehd"].use_custom_rank else settings.custom_ranks["audio"]["truehd"].rank
            case "HQ Clean Audio":
                total_rank += rank_model.clean_audio if not settings.custom_ranks["trash"]["clean_audio"].use_custom_rank else settings.custom_ranks["trash"]["clean_audio"].rank
            case _:
                total_rank += 0

    return total_rank


def calculate_channels_rank(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate the channels ranking of the given parsed data."""
    if not data.channels:
        return 0
    
    total_rank = 0
    for channel in data.channels:
        match channel:
            case "5.1" | "7.1":
                total_rank += rank_model.surround if not settings.custom_ranks["audio"]["surround"].use_custom_rank else settings.custom_ranks["audio"]["surround"].rank
            case "stereo" | "2.0":
                total_rank += rank_model.stereo if not settings.custom_ranks["audio"]["stereo"].use_custom_rank else settings.custom_ranks["audio"]["stereo"].rank
            case "mono":
                total_rank += rank_model.mono if not settings.custom_ranks["audio"]["mono"].use_custom_rank else settings.custom_ranks["audio"]["mono"].rank
            case _:
                total_rank += 0

    return total_rank


def calculate_extra_ranks(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate all the other rankings of the given parsed data."""
    if not data.bit_depth and not data.hdr and not data.seasons and not data.episodes:
        return 0

    total_rank = 0

    if data._3d:
        total_rank += rank_model.remux if not settings.custom_ranks["extras"]["3d"].use_custom_rank else settings.custom_ranks["extras"]["3d"].rank
    if data.converted:
        total_rank += rank_model.converted if not settings.custom_ranks["extras"]["converted"].use_custom_rank else settings.custom_ranks["extras"]["converted"].rank
    if data.documentary:
        total_rank += rank_model.documentary if not settings.custom_ranks["extras"]["documentary"].use_custom_rank else settings.custom_ranks["extras"]["documentary"].rank
    if data.dubbed:
        total_rank += rank_model.dubbed if not settings.custom_ranks["extras"]["dubbed"].use_custom_rank else settings.custom_ranks["extras"]["dubbed"].rank
    if data.edition:
        total_rank += rank_model.edition if not settings.custom_ranks["extras"]["edition"].use_custom_rank else settings.custom_ranks["extras"]["edition"].rank
    if data.hardcoded:
        total_rank += rank_model.hardcoded if not settings.custom_ranks["extras"]["hardcoded"].use_custom_rank else settings.custom_ranks["extras"]["hardcoded"].rank
    if data.network:
        total_rank += rank_model.network if not settings.custom_ranks["extras"]["network"].use_custom_rank else settings.custom_ranks["extras"]["network"].rank
    if data.proper:
        total_rank += rank_model.proper if not settings.custom_ranks["extras"]["proper"].use_custom_rank else settings.custom_ranks["extras"]["proper"].rank
    if data.repack:
        total_rank += rank_model.repack if not settings.custom_ranks["extras"]["repack"].use_custom_rank else settings.custom_ranks["extras"]["repack"].rank
    if data.retail:
        total_rank += rank_model.retail if not settings.custom_ranks["extras"]["retail"].use_custom_rank else settings.custom_ranks["extras"]["retail"].rank
    if data.subbed:
        total_rank += rank_model.subbed if not settings.custom_ranks["extras"]["subbed"].use_custom_rank else settings.custom_ranks["extras"]["subbed"].rank
    if data.upscaled:
        total_rank += rank_model.upscaled if not settings.custom_ranks["extras"]["upscaled"].use_custom_rank else settings.custom_ranks["extras"]["upscaled"].rank
    if data.site:
        total_rank += rank_model.site if not settings.custom_ranks["extras"]["site"].use_custom_rank else settings.custom_ranks["extras"]["site"].rank
    if data.size:
        total_rank += rank_model.size if not settings.custom_ranks["trash"]["size"].use_custom_rank else settings.custom_ranks["trash"]["size"].rank
    return total_rank
