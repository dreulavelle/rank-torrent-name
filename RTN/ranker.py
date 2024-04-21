"""
This module contains functions to rank parsed data based on user settings and custom ranking models.

Functions:
- `get_rank`: Calculate the ranking of the given parsed data.
- `calculate_preferred`: Calculate the preferred ranking of a given parsed data.
- `calculate_resolution_rank`: Calculate the resolution ranking of the given parsed data.
- `calculate_quality_rank`: Calculate the quality ranking of the given parsed data.
- `calculate_codec_rank`: Calculate the codec ranking of the given parsed data.
- `calculate_audio_rank`: Calculate the audio ranking of the given parsed data.
- `calculate_other_ranks`: Calculate all the other rankings of the given parsed data.

Arguments:
- `data` (ParsedData): The parsed data object containing information about the torrent title.
- `settings` (SettingsModel): The user settings object containing custom ranking models.
- `rank_model` (BaseRankingModel): The base ranking model used for calculating the ranking.

For more information on each function, refer to the respective docstrings.

Examples:
    >>> get_rank(ParsedData, SettingsModel, BaseRankingModel)
    250
    >>> calculate_preferred(ParsedData, SettingsModel)
    5000
    >>> calculate_resolution_rank(ParsedData, SettingsModel, BaseRankingModel)
    25
    >>> calculate_quality_rank(ParsedData, SettingsModel, BaseRankingModel)
    20
    >>> calculate_codec_rank(ParsedData, SettingsModel, BaseRankingModel)
    10
    >>> calculate_audio_rank(ParsedData, SettingsModel, BaseRankingModel)
    5
    >>> calculate_other_ranks(ParsedData, SettingsModel, BaseRankingModel)
    25
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

    rank: int = calculate_resolution_rank(data, settings, rank_model)
    rank += calculate_quality_rank(data, settings, rank_model)
    rank += calculate_codec_rank(data, settings, rank_model)
    rank += calculate_audio_rank(data, settings, rank_model)
    rank += calculate_other_ranks(data, settings, rank_model)
    rank += calculate_preferred(data, settings)
    if data.repack:
        rank += rank_model.repack if not settings.custom_ranks["repack"].enable else settings.custom_ranks["repack"].rank
    if data.proper:
        rank += rank_model.proper if not settings.custom_ranks["proper"].enable else settings.custom_ranks["proper"].rank
    if data.remux:
        rank += rank_model.remux if not settings.custom_ranks["remux"].enable else settings.custom_ranks["remux"].rank
    if data.is_multi_audio:
        rank += rank_model.dubbed if not settings.custom_ranks["dubbed"].enable else settings.custom_ranks["dubbed"].rank
    if data.is_multi_subtitle:
        rank += rank_model.subbed if not settings.custom_ranks["subbed"].enable else settings.custom_ranks["subbed"].rank
    return rank


def calculate_preferred(data: ParsedData, settings: SettingsModel) -> int:
    """Calculate the preferred ranking of a given parsed data."""
    if not settings.preferred or all(pattern is None for pattern in settings.preferred):
        return 0
    return 5000 if any(pattern.search(data.raw_title) for pattern in settings.preferred if pattern) else 0  # type: ignore


def calculate_resolution_rank(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate the resolution ranking of the given parsed data."""
    if not data.resolution:
        return 0

    resolution: str = data.resolution[0]
    match resolution:
        case "4K":
            return rank_model.uhd if not settings.custom_ranks["uhd"].enable else settings.custom_ranks["uhd"].rank
        case "2160p":
            return rank_model.uhd if not settings.custom_ranks["uhd"].enable else settings.custom_ranks["uhd"].rank
        case "1440p":
            return rank_model.uhd if not settings.custom_ranks["uhd"].enable else settings.custom_ranks["uhd"].rank
        case "1080p":
            return rank_model.fhd if not settings.custom_ranks["fhd"].enable else settings.custom_ranks["fhd"].rank
        case "720p":
            return rank_model.hd if not settings.custom_ranks["hd"].enable else settings.custom_ranks["hd"].rank
        case "576p" | "480p":
            return rank_model.sd if not settings.custom_ranks["sd"].enable else settings.custom_ranks["sd"].rank
        case _:
            return 0


def calculate_quality_rank(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate the quality ranking of the given parsed data."""
    if not data.quality:
        return 0

    quality = data.quality[0]
    match quality:
        case "WEB-DL":
            return rank_model.webdl if not settings.custom_ranks["webdl"].enable else settings.custom_ranks["webdl"].rank
        case "Blu-ray":
            return rank_model.bluray if not settings.custom_ranks["bluray"].enable else settings.custom_ranks["bluray"].rank
        case "WEBCap" | "Cam" | "Telesync" | "Telecine" | "Screener" | "VODRip" | "TVRip" | "DVD-R":
            return -1000
        case "BDRip":
            return 5  # This one's a little better than BRRip
        case "BRRip":
            return 0
        case _:
            return 0


def calculate_codec_rank(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate the codec ranking of the given parsed data."""
    if not data.codec:
        return 0

    codec = data.codec[0]
    match codec:
        case "Xvid" | "H.263" | "VC-1" | "MPEG-2":
            return -1000
        case "AV1":
            return rank_model.av1 if not settings.custom_ranks["av1"].enable else settings.custom_ranks["av1"].rank
        case "H.264":
            return 3
        case "H.265" | "H.265 Main 10" | "HEVC":
            return 0
        case _:
            return 0


def calculate_audio_rank(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate the audio ranking of the given parsed data."""
    if not data.audio:
        return 0

    audio_format: str = data.audio[0]

    # Remove any unwanted audio formats. We dont support surround sound formats yet.
    # These also make it harder to compare audio formats.
    audio_format = regex.sub(r"7.1|5.1|Dual|Mono|Original|LiNE", "", audio_format).strip()
    match audio_format:
        case "Dolby TrueHD":
            return rank_model.truehd if not settings.custom_ranks["truehd"].enable else settings.custom_ranks["truehd"].rank
        case "Dolby Atmos":
            return rank_model.atmos if not settings.custom_ranks["atmos"].enable else settings.custom_ranks["atmos"].rank
        case "Dolby Digital":
            return rank_model.ac3 if not settings.custom_ranks["ac3"].enable else settings.custom_ranks["ac3"].rank
        case "Dolby Digital EX":
            return rank_model.dts_x if not settings.custom_ranks["dts_x"].enable else settings.custom_ranks["dts_x"].rank
        case "Dolby Digital Plus":
            return rank_model.ddplus if not settings.custom_ranks["ddplus"].enable else settings.custom_ranks["ddplus"].rank
        case "DTS":
            return rank_model.dts_hd if not settings.custom_ranks["dts_hd"].enable else settings.custom_ranks["dts_hd"].rank
        case "DTS-HD":
            return (
                (rank_model.dts_hd + 5) if not settings.custom_ranks["dts_hd"].enable else settings.custom_ranks["dts_hd"].rank
            )
        case "DTS-HD MA":
            return (
                (rank_model.dts_hd_ma + 10)
                if not settings.custom_ranks["dts_hd_ma"].enable
                else settings.custom_ranks["dts_hd_ma"].rank
            )
        case "DTS-ES" | "DTS-EX":
            return rank_model.dts_x + 5 if not settings.custom_ranks["dts_x"].enable else settings.custom_ranks["dts_x"].rank
        case "DTS:X":
            return rank_model.dts_x + 10 if not settings.custom_ranks["dts_x"].enable else settings.custom_ranks["dts_x"].rank
        case "AAC":
            return rank_model.aac if not settings.custom_ranks["aac"].enable else settings.custom_ranks["aac"].rank
        case "AAC-LC":
            return rank_model.aac + 2 if not settings.custom_ranks["aac"].enable else settings.custom_ranks["aac"].rank
        case "HE-AAC":
            return rank_model.aac + 5 if not settings.custom_ranks["aac"].enable else settings.custom_ranks["aac"].rank
        case "HE-AAC v2":
            return rank_model.aac + 10 if not settings.custom_ranks["aac"].enable else settings.custom_ranks["aac"].rank
        case "AC3":
            return rank_model.ac3 if not settings.custom_ranks["ac3"].enable else settings.custom_ranks["ac3"].rank
        case "FLAC" | "OGG":
            return -1000
        case _:
            return 0


def calculate_other_ranks(data: ParsedData, settings: SettingsModel, rank_model: BaseRankingModel) -> int:
    """Calculate all the other rankings of the given parsed data."""
    if not data.bitDepth and not data.hdr and not data.is_complete and not data.season and not data.episode:
        return 0

    total_rank = 0
    if data.bitDepth and data.bitDepth[0] >= 8:
        total_rank += 2
    if data.hdr:
        if data.hdr == "HDR":
            total_rank += settings.custom_ranks["hdr"].rank if settings.custom_ranks["hdr"].enable else rank_model.hdr
        elif data.hdr == "HDR10+":
            total_rank += settings.custom_ranks["hdr10"].rank if settings.custom_ranks["hdr10"].enable else rank_model.hdr10
        elif data.hdr == "DV":
            total_rank += (
                settings.custom_ranks["dolby_video"].rank
                if settings.custom_ranks["dolby_video"].enable
                else rank_model.dolby_video
            )
    if data.is_complete:
        total_rank += 100
    if len(data.season) > 0 and len(data.episode) == 0:
        total_rank += 125 * len(data.season)
    if len(data.episode) > 0:
        total_rank += 10 * len(data.episode)
    return total_rank
