"""
This module contains models used in the RTN package for parsing torrent titles, ranking media quality, and defining user settings.

Models:
- `ParsedData`: Model for storing parsed information from a torrent title.
- `BaseRankingModel`: Base class for ranking models used in the context of media quality and attributes.
- `Torrent`: Model for representing a torrent with metadata parsed from its title and additional computed properties.
- `DefaultRanking`: Default ranking model preset that covers the most common use cases.
- `BestRanking`: Ranking model preset that prioritizes the highest quality and most desirable attributes.
- `CustomRank`: Model used in the `SettingsModel` for defining custom ranks for specific attributes.
- `SettingsModel`: User-defined settings model for ranking torrents, including preferences for filtering torrents based on regex patterns and customizing ranks for specific torrent attributes.

For more information on each model, refer to the respective docstrings.

Note:
- The `ParsedData` model contains attributes for storing parsed information from a torrent title.
- The `BaseRankingModel` model is a base class for ranking models used in the context of media quality and attributes.
- The `CustomRank` model is used in the `SettingsModel` for defining custom ranks for specific attributes.
- The `SettingsModel` model allows users to define custom settings for ranking torrents based on quality attributes and regex patterns.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

import regex
from pydantic import BaseModel, field_validator, model_validator
from regex import Pattern

from RTN.exceptions import GarbageTorrent


class ParsedData(BaseModel):
    """Parsed data model for a torrent title."""

    raw_title: str
    parsed_title: str = ""
    normalized_title: str = ""
    trash: bool = False
    year: Optional[int] = None
    resolution: str = "unknown"
    seasons: List[int] = []
    episodes: List[int] = []
    complete: bool = False
    volumes: List[int] = []
    languages: List[str] = []
    quality: Optional[str] = None
    hdr: List[str] = []
    codec: Optional[str] = None
    audio: List[str] = []
    channels: List[str] = []
    dubbed: bool = False
    subbed: bool = False
    date: Optional[str] = None
    group: Optional[str] = None
    edition: Optional[str] = None
    bit_depth: Optional[str] = None
    bitrate: Optional[str] = None
    network: Optional[str] = None
    extended: bool = False
    converted: bool = False
    hardcoded: bool = False
    region: Optional[str] = None
    ppv: bool = False
    _3d: bool = False
    site: Optional[str] = None
    size: Optional[str] = None
    proper: bool = False
    repack: bool = False
    retail: bool = False
    upscaled: bool = False
    remastered: bool = False
    unrated: bool = False
    documentary: bool = False
    episode_code: Optional[str] = None
    country: Optional[str] = None
    container: Optional[str] = None
    extension: Optional[str] = None
    extras: List[str] = []
    torrent: bool = False

    class Config:
        from_attributes = True
        use_orm = True

    @property
    def type(self) -> str:
        """Returns the type of the torrent based on its attributes."""
        if not self.seasons and not self.episodes:
            return "movie"
        return "show"

    def to_dict(self):
        return self.model_dump_json()

class Torrent(BaseModel):
    """
    Represents a torrent with metadata parsed from its title and additional computed properties.

    Attributes:
        `raw_title` (str): The original title of the torrent.
        `infohash` (str): The SHA-1 hash identifier of the torrent.
        `data` (ParsedData): Metadata extracted from the torrent title.
        `fetch` (bool): Indicates whether the torrent meets the criteria for fetching based on user settings.
        `rank` (int): The computed ranking score of the torrent based on user-defined preferences.
        `lev_ratio` (float): The Levenshtein ratio comparing the parsed title and the raw title for similarity.

    Methods:
        __eq__: Determines equality based on the infohash of the torrent, allowing for easy comparison.
        __hash__: Generates a hash based on the infohash of the torrent for set operations.
    
    Raises:
        `GarbageTorrent`: If the title is identified as trash and should be ignored by the scraper.

    Example:
        >>> torrent = Torrent(
        ...     raw_title="The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]",
        ...     infohash="c08a9ee8ce3a5c2c08865e2b05406273cabc97e7",
        ...     data=ParsedData(...),
        ...     fetch=True,
        ...     rank=500,
        ...     lev_ratio=0.95,
        ... )
        >>> isinstance(torrent, Torrent)
        True
        >>> torrent.raw_title
        'The Walking Dead S05E03 720p HDTV x264-ASAP[ettv]'
        >>> torrent.infohash
        'c08a9ee8ce3a5c2c08865e2b05406273cabc97e7'
        >>> torrent.data.parsed_title
        'The Walking Dead'
        >>> torrent.fetch
        True
        >>> torrent.rank
        500
        >>> torrent.lev_ratio
        0.95
    """

    infohash: str
    raw_title: str
    torrent: Optional[str] = None
    seeders: Optional[int] = 0
    leechers: Optional[int] = 0
    trackers: Optional[List[Any]] = []
    data: ParsedData
    fetch: bool = False
    rank: int = 0
    lev_ratio: float = 0.0

    class Config:
        from_attributes = True
        use_orm = True
        frozen = True

    @field_validator("infohash")
    def validate_infohash(cls, v):
        """Validates infohash length and format (MD5 or SHA-1)."""
        if len(v) not in (32, 40) or not regex.match(r"^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{40}$", v):
            raise GarbageTorrent("Infohash must be a 32-character MD5 hash or a 40-character SHA-1 hash.")
        return v

    def __eq__(self, other: object) -> bool:
        """Compares Torrent objects based on their infohash."""
        return isinstance(other, Torrent) and self.infohash == other.infohash

    def __hash__(self) -> int:
        return hash(self.infohash)

    def to_dict(self):
        return self.model_dump_json()

class BaseRankingModel(BaseModel):
    """
    A base class for ranking models used in the context of media quality and attributes.
    The ranking values are used to determine the quality of a media item based on its attributes.

    Note:
        - The higher the ranking value, the better the quality of the media item.
        - The default ranking values are set to 0, which means that the attribute does not affect the overall rank.
        - Users can customize the ranking values based on their preferences and requirements by using inheritance.
    """
    # quality
    av1: int = 0
    avc: int = 0
    bluray: int = 0
    dvd: int = 0
    hdtv: int = 0
    hevc: int = 0
    mpeg: int = 0
    remux: int = 0
    vhs: int = 0
    web: int = 0
    webdl: int = 0
    webmux: int = 0
    xvid: int = 0

    # rips
    bdrip: int = 0
    brrip: int = 0
    dvdrip: int = 0
    hdrip: int = 0
    ppvrip: int = 0
    tvrip: int = 0
    uhdrip: int = 0
    vhsrip: int = 0
    webdlrip: int = 0
    webrip: int = 0

    # hdr
    bit_10: int = 0
    dolby_vision: int = 0
    hdr: int = 0
    hdr10plus: int = 0
    sdr: int = 0

    # audio
    aac: int = 0
    ac3: int = 0
    atmos: int = 0
    dolby_digital: int = 0
    dolby_digital_plus: int = 0
    dts_lossy: int = 0
    dts_lossless: int = 0
    eac3: int = 0
    flac: int = 0
    mono: int = 0
    mp3: int = 0
    stereo: int = 0
    surround: int = 0
    truehd: int = 0

    # extras
    three_d: int = 0
    converted: int = 0
    documentary: int = 0
    dubbed: int = 0
    edition: int = 0
    hardcoded: int = 0
    network: int = 0
    proper: int = 0
    repack: int = 0
    retail: int = 0
    subbed: int = 0
    upscaled: int = 0

    # trash
    cam: int = 0
    clean_audio: int = 0
    r5: int = 0
    pdtv: int = 0
    satrip: int = 0
    screener: int = 0
    site: int = 0
    size: int = 0
    telecine: int = 0
    telesync: int = 0


class DefaultRanking(BaseRankingModel):
    """Ranking model preset that covers the most common use cases."""

    # quality
    av1: int = 0
    avc: int = 500
    bluray: int = 100
    dvd: int = -1000
    hdtv: int = -1000
    hevc: int = 500
    mpeg: int = -100
    remux: int = -10000
    vhs: int = -10000
    web: int = 150
    webdl: int = 5000
    webmux: int = -10000
    xvid: int = -10000
    pdtv: int = -10000

    # rips
    bdrip: int = -1000
    brrip: int = -1000
    dvdrip: int = -1000
    hdrip: int = -1000
    ppvrip: int = -1000
    tvrip: int = -10000
    uhdrip: int = -1000
    vhsrip: int = -10000
    webdlrip: int = -10000
    webrip: int = 30

    # hdr
    bit_10: int = 5
    dolby_vision: int = 50
    hdr: int = 50
    hdr10plus: int = 0
    sdr: int = 0

    # audio
    aac: int = 250
    ac3: int = 30
    atmos: int = 400
    dolby_digital: int = 0
    dolby_digital_plus: int = 0
    dts_lossy: int = 600
    dts_lossless: int = 0
    eac3: int = 250
    flac: int = 0
    mono: int = -10000
    mp3: int = -10000
    stereo: int = 0
    surround: int = 0
    truehd: int = -100

    # extras
    three_d: int = -10000
    converted: int = -1250
    documentary: int = -250
    dubbed: int = 0
    edition: int = 100
    hardcoded: int = 0
    network: int = 300
    proper: int = 1000
    repack: int = 1000
    retail: int = 0
    site: int = -10000
    subbed: int = 0
    upscaled: int = -10000

    # trash
    cam: int = -10000
    clean_audio: int = -10000
    r5: int = -10000
    satrip: int = -10000
    screener: int = -10000
    size: int = -10000
    telecine: int = -10000
    telesync: int = -10000


class BestRanking(BaseRankingModel):
    """Ranking model preset that covers the highest qualities like 4K HDR."""

    # quality
    av1: int = 0
    avc: int = 500
    bluray: int = 100
    dvd: int = -5000
    hdtv: int = -5000
    hevc: int = 500
    mpeg: int = -1000
    remux: int = 10000
    vhs: int = -10000
    web: int = 100
    webdl: int = 200
    webmux: int = -10000
    xvid: int = -10000
    pdtv: int = -10000

    # rips
    bdrip: int = -5000
    brrip: int = -10000
    dvdrip: int = -5000
    hdrip: int = -10000
    ppvrip: int = -10000
    tvrip: int = -10000
    uhdrip: int = -5000
    vhsrip: int = -10000
    webdlrip: int = -10000
    webrip: int = -1000

    # hdr
    bit_10: int = 100
    dolby_vision: int = 1000
    hdr: int = 500
    hdr10plus: int = 1000
    sdr: int = 0

    # audio
    aac: int = 100
    ac3: int = 50
    atmos: int = 1000
    dolby_digital: int = 0
    dolby_digital_plus: int = 0
    dts_lossy: int = 100
    dts_lossless: int = 1000
    eac3: int = 150
    flac: int = 0
    mono: int = -1000
    mp3: int = -1000
    stereo: int = 0
    surround: int = 0
    truehd: int = 1000

    # extras
    three_d: int = -10000
    converted: int = -1000
    documentary: int = -250
    dubbed: int = -1000
    edition: int = 100
    hardcoded: int = 0
    network: int = 0
    proper: int = 20
    repack: int = 20
    retail: int = 0
    site: int = -10000
    subbed: int = 0
    upscaled: int = -10000

    # trash
    cam: int = -10000
    clean_audio: int = -10000
    r5: int = -10000
    satrip: int = -10000
    screener: int = -10000
    size: int = -10000
    telecine: int = -10000
    telesync: int = -10000


class Resolution(str, Enum):
    UHD = "4k"
    UHD_2160P = "2160p"
    UHD_1440P = "1440p"
    FHD = "1080p"
    HD = "720p"
    SD_576P = "576p"
    SD_480P = "480p"
    SD_360P = "360p"
    UNKNOWN = "unknown"  # default


class CustomRank(BaseModel):
    """Custom Ranks used in SettingsModel."""
    fetch: bool = True
    use_custom_rank: bool = False
    rank: int = 0


class SettingsModel(BaseModel):
    """
    Represents user-defined settings for ranking torrents, including preferences for filtering torrents
    based on regex patterns and customizing ranks for specific torrent attributes. This model allows for
    advanced customization and fine-grained control over the ranking process.

    Attributes:
        profile (str): Identifier for the settings profile, allowing for multiple configurations.
        require (List[str | Pattern]): Patterns torrents must match to be considered.
        exclude (List[str | Pattern]): Patterns that, if matched, result in torrent exclusion.
        preferred (List[str | Pattern]): Patterns indicating preferred attributes in torrents. Given +5000 points by default.
        custom_ranks (Dict[str, Dict[str, CustomRank]]): Custom ranking configurations for specific attributes, allowing users to define how different torrent qualities and features affect the overall rank.

    Methods:
        __init__(**kwargs): Initializes the settings model with user-defined preferences. Automatically compiles string regex patterns into Patterns, taking into account case sensitivity based on the pattern syntax.
        __getitem__(item: str) -> CustomRank: Access custom rank settings via attribute keys.

    Note:
        - The `profile` attribute allows users to define multiple settings profiles for different use cases.
        - The `require`, `exclude`, and `preferred` attributes are optional!
        - The `custom_ranks` attribute contains default values for common torrent attributes, which can be customized by users.
        - Patterns enclosed in '/' without a trailing 'i' are compiled as case-sensitive.
        - Patterns not enclosed are compiled as case-insensitive by default.

    This model supports advanced regex features, enabling powerful and precise filtering and ranking based on torrent titles and attributes.

    Example:
        >>> settings = SettingsModel(
                profile="default",
                require=["\\b4K|1080p\\b", "720p"],
                exclude=["CAM", "TS"],
                preferred=["BluRay", r"/\\bS\\d+/", "/HDR|HDR10/"],
                ...
                },
            )
        >>> print([pattern.pattern for pattern in settings.require])
        ['\\b4K|1080p\\b', '720p']
        >>> print([pattern.pattern for pattern in settings.preferred])
        ['BluRay', '\\bS\\d+', 'HDR|HDR10']
        >>> print(settings.custom_ranks["uhd"].rank)
        150
    """

    profile: str = "default"
    require: List[str | Pattern] = []
    exclude: List[str | Pattern] = []
    preferred: List[str | Pattern] = []
    resolutions: Dict[str, bool] = {
        "2160p": False,
        "1080p": True,
        "720p": True,
        "480p": False,
        "360p": False,
        "unknown": True
    }
    options: Dict[str, Any] = {
        "title_similarity": 0.85,
        "remove_all_trash": True,
        "remove_ranks_under": -10000,
        "remove_unknown_languages": False,
        "allow_english_in_languages": False
    }
    languages: Dict[str, Any] = {
        "required": [],
        "exclude": ["common"],
        "preferred": [],
    }
    custom_ranks: Dict[str, Dict[str, CustomRank]] = {
        "quality": {
            "av1": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "avc": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "bluray": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "dvd": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "hdtv": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "hevc": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "mpeg": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "remux": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "vhs": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "web": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "webdl": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "webmux": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "xvid": CustomRank(fetch=False, use_custom_rank=False, rank=0),
        },
        "rips": {
            "bdrip": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "brrip": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "dvdrip": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "hdrip": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "ppvrip": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "satrip": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "tvrip": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "uhdrip": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "vhsrip": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "webdlrip": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "webrip": CustomRank(fetch=True, use_custom_rank=False, rank=0),
        },
        "hdr": {
            "10bit": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "dolby_vision": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "hdr": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "hdr10plus": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "sdr": CustomRank(fetch=True, use_custom_rank=False, rank=0),
        },
        "audio": {
            "aac": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "ac3": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "atmos": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "dolby_digital": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "dolby_digital_plus": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "dts_lossy": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "dts_lossless": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "eac3": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "flac": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "mono": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "mp3": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "stereo": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "surround": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "truehd": CustomRank(fetch=True, use_custom_rank=False, rank=0),
        },
        "extras": {
            "3d": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "converted": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "documentary": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "dubbed": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "edition": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "hardcoded": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "network": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "proper": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "repack": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "retail": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "site": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "subbed": CustomRank(fetch=True, use_custom_rank=False, rank=0),
            "upscaled": CustomRank(fetch=False, use_custom_rank=False, rank=0),
        },
        "trash": {
            "cam": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "clean_audio": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "pdtv": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "r5": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "screener": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "size": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "telecine": CustomRank(fetch=False, use_custom_rank=False, rank=0),
            "telesync": CustomRank(fetch=False, use_custom_rank=False, rank=0)
        },
    }

    @model_validator(mode="before")
    def compile_and_validate_patterns(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Compile string patterns to regex.Pattern, keeping compiled patterns unchanged."""
        for field in ("require", "exclude", "preferred"):
            raw_patterns = values.get(field, [])
            compiled_patterns = []
            for pattern in raw_patterns:
                if isinstance(pattern, str):
                    if pattern.startswith("/") and pattern.endswith("/"):  # case-sensitive
                        compiled_patterns.append(regex.compile(pattern[1:-1]))
                    else:  # case-insensitive by default
                        compiled_patterns.append(regex.compile(pattern, regex.IGNORECASE))
                elif isinstance(pattern, regex.Pattern):
                    # Keep already compiled patterns as is
                    compiled_patterns.append(pattern)
                else:
                    raise ValueError(f"Invalid pattern type: {type(pattern)}")
            values[field] = compiled_patterns
        return values

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Pattern: lambda v: v.pattern
        }
