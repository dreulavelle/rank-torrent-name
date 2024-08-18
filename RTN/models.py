"""
This module contains models used in the RTN package for parsing torrent titles, ranking media quality, and defining user settings.

Models:
- `ParsedData`: Parsed data model for a torrent title.
- `BaseRankingModel`: Base class for ranking models used in the context of media quality and attributes.
- `CustomRank`: Custom ranking model used in the `SettingsModel` for defining custom ranks for specific attributes.
- `SettingsModel`: User-defined settings model for ranking torrents, including preferences for filtering torrents based on regex patterns and customizing ranks for specific torrent attributes.

For more information on each model, refer to the respective docstrings.

Note:
- The `ParsedData` model contains attributes for storing parsed information from a torrent title.
- The `BaseRankingModel` model is a base class for ranking
- The `CustomRank` model is used in the `SettingsModel` for defining custom ranks for specific attributes.
- The `SettingsModel` model allows users to define custom settings for ranking torrents based on quality attributes and regex patterns.

Example:
    >>> rank_model = DefaultRanking()
    >>> settings = SettingsModel(
            profile="default",
            require=["\\b4K|1080p\\b", "720p"],
            exclude=["CAM", "TS"],
            preferred=["BluRay", r"/\\bS\\d+/", "/HDR|HDR10/i"],
            custom_ranks={
                "uhd": CustomRank(enable=True, fetch=False, rank=150),
                "fhd": CustomRank(enable=True, fetch=True, rank=90),
                ...
            },
        )
    >>> rtn = RTN(rank_model, settings)
"""

from typing import Any, Dict, List, Optional, Union

import regex
from pydantic import BaseModel, field_validator, model_validator, root_validator
from regex import Pattern

from PTT import parse_title

from RTN.exceptions import GarbageTorrent


class ParsedData(BaseModel):
    """Parsed data model for a torrent title."""

    raw_title: str
    parsed_title: str
    normalized_title: str = None
    trash: bool = False
    year: int = None
    resolution: str = "unknown"
    seasons: List[int] = []
    episodes: List[int] = []
    complete: bool = False
    volumes: List[int] = []
    languages: List[str] = []
    quality: str = None
    hdr: List[str] = []
    codec: str = None
    audio: List[str] = []
    channels: List[str] = []
    dubbed: bool = False
    subbed: bool = False
    date: str = None
    group: str = None
    edition: str = None
    bit_depth: str = None
    bitrate: str = None
    extended: bool = False
    convert: bool = False
    hardcoded: bool = False
    region: str = None
    ppv: bool = False
    site: str = None
    proper: bool = False
    repack: bool = False
    retail: bool = False
    upscaled: bool = False
    remastered: bool = False
    unrated: bool = False
    documentary: bool = False
    episode_code: str = None
    country: str = None
    container: str = None
    extension: str = None
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

    Attributes:
        `uhd` (int): The ranking value for Ultra HD (4K) resolution.
        `fhd` (int): The ranking value for Full HD (1080p) resolution.
        `hd` (int): The ranking value for HD (720p) resolution.
        `sd` (int): The ranking value for SD (480p) resolution.
        `bluray` (int): The ranking value for Blu-ray quality.
        `hdr` (int): The ranking value for HDR quality.
        `hdr10` (int): The ranking value for HDR10 quality.
        `dolby_video` (int): The ranking value for Dolby video quality.
        `dts_x` (int): The ranking value for DTS:X audio quality.
        `dts_hd` (int): The ranking value for DTS-HD audio quality.
        `dts_hd_ma` (int): The ranking value for DTS-HD Master Audio audio quality.
        `atmos` (int): The ranking value for Dolby Atmos audio quality.
        `truehd` (int): The ranking value for Dolby TrueHD audio quality.
        `ddplus` (int): The ranking value for Dolby Digital Plus audio quality.
        `ac3` (int): The ranking value for AC3 audio quality.
        `aac` (int): The ranking value for AAC audio quality.
        `remux` (int): The ranking value for remux attribute.
        `webdl` (int): The ranking value for web-dl attribute.
        `repack` (int): The ranking value for repack attribute.
        `proper` (int): The ranking value for proper attribute.
        `dubbed` (int): The ranking value for dubbed attribute.
        `subbed` (int): The ranking value for subbed attribute.
        `av1` (int): The ranking value for AV1 attribute.

    Note:
        - The higher the ranking value, the better the quality of the media item.
        - The default ranking values are set to 0, which means that the attribute does not affect the overall rank.
        - Users can customize the ranking values based on their preferences and requirements by using inheritance.
    """

    # resolution
    uhd: int = 0  # 4K
    fhd: int = 0  # 1080p
    hd: int = 0  # 720p
    sd: int = 0  # 480p
    # quality
    bluray: int = 0
    hdr: int = 0
    hdr10: int = 0
    dolby_video: int = 0
    # codec
    h264: int = 0
    h265: int = 0
    hevc: int = 0
    avc: int = 0
    av1: int = 0
    # audio
    dts_x: int = 0
    dts_hd: int = 0
    dts_hd_ma: int = 0
    atmos: int = 0
    truehd: int = 0
    ddplus: int = 0
    ac3: int = 0
    aac: int = 0
    # other
    remux: int = 0
    webdl: int = 0
    dvdrip: int = 0
    bdrip: int = 0
    brrip: int = 0
    hdtv: int = 0
    repack: int = 5
    proper: int = 4
    # languages
    dubbed: int = 4
    subbed: int = 2


class DefaultRanking(BaseRankingModel):
    """Default ranking model preset that should cover most common use cases."""

    uhd: int = 140
    fhd: int = 100
    hd: int = 50
    sd: int = -100
    dolby_video: int = -1000
    hdr: int = -1000
    hdr10: int = -1000
    aac: int = 70
    ac3: int = 50
    remux: int = -1000
    webdl: int = 90
    bluray: int = -90


class CustomRank(BaseModel):
    """Custom Ranks used in SettingsModel."""

    enable: bool = False
    fetch: bool = False
    rank: int = 0


class SettingsModel(BaseModel):
    """
    Represents user-defined settings for ranking torrents, including preferences for filtering torrents
    based on regex patterns and customizing ranks for specific torrent attributes. This model allows for
    advanced customization and fine-grained control over the ranking process.

    Attributes:
        `profile` (str): Identifier for the settings profile, allowing for multiple configurations.
        `require` (List[Union[str, Pattern]]): Patterns torrents must match to be considered.
        `exclude` (List[Union[str, Pattern]]): Patterns that, if matched, result in torrent exclusion.
        `preferred` (List[Union[str, Pattern]]): Patterns indicating preferred attributes in torrents. Given +5000 points by default.
        `custom_ranks` (Dict[str, CustomRank]): Custom ranking configurations for specific attributes, allowing users to define
                                              how different torrent qualities and features affect the overall rank.

    Methods:
        __init__(**kwargs): Initializes the settings model with user-defined preferences. Automatically compiles string
                            regex patterns into Patterns, taking into account case sensitivity based on the pattern syntax.
        __getitem__(item: str) -> CustomRank: Access custom rank settings via attribute keys.

    Note:
        - The `profile` attribute allows users to define multiple settings profiles for different use cases.
        - The `require`, `exclude`, and `preferred` attributes are optional! If not provided, they default to an empty list.
        - The `custom_ranks` attribute contains default values for common torrent attributes, which can be customized by users.
        - Patterns enclosed in '/' without a trailing 'i' are compiled as case-sensitive.
        - Patterns enclosed in '/' with a trailing 'i' are compiled as case-insensitive.
        - Patterns not enclosed are compiled as case-insensitive by default.

    This model supports advanced regex features, enabling powerful and precise filtering and ranking based on torrent titles and attributes.

    Example:
        >>> settings = SettingsModel(
                profile="default",
                require=["\\b4K|1080p\\b", "720p"],
                exclude=["CAM", "TS"],
                preferred=["BluRay", r"/\\bS\\d+/", "/HDR|HDR10/i"],
                custom_ranks={
                    "uhd": CustomRank(enable=True, fetch=False, rank=150),
                    "fhd": CustomRank(enable=True, fetch=True, rank=90),
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
    require: List[Union[str, Pattern]] = []
    exclude: List[Union[str, Pattern]] = []
    preferred: List[Union[str, Pattern]] = []
    options: Dict[str, Any] = {
        "lev_ratio": 0.821,
        "remove_trash": True,
        "strict_mode": False,
        "allow_unknown_resolutions": True,
    }
    languages: Dict[str, Any] = {
        "allow_unknown_languages": True,
        "require": [],
        "exclude": ["hi", "ta"],
        "preferred": [],
    }
    custom_ranks: Dict[str, CustomRank] = {
        "uhd": CustomRank(enable=False, fetch=True, rank=120),
        "fhd": CustomRank(enable=False, fetch=True, rank=90),
        "hd": CustomRank(enable=False, fetch=True, rank=80),
        "sd": CustomRank(enable=False, fetch=True, rank=-120),
        "hdr": CustomRank(enable=False, fetch=True, rank=40),
        "hdr10": CustomRank(enable=False, fetch=True, rank=50),
        "dolby_video": CustomRank(enable=False, fetch=True, rank=-100),
        "h264": CustomRank(enable=False, fetch=True, rank=0),
        "h265": CustomRank(enable=False, fetch=True, rank=0),
        "hevc": CustomRank(enable=False, fetch=True, rank=0),
        "avc": CustomRank(enable=False, fetch=True, rank=0),
        "av1": CustomRank(enable=False, fetch=True, rank=0),
        "dts_x": CustomRank(enable=False, fetch=True, rank=0),
        "dts_hd": CustomRank(enable=False, fetch=True, rank=0),
        "dts_hd_ma": CustomRank(enable=False, fetch=True, rank=0),
        "atmos": CustomRank(enable=False, fetch=True, rank=0),
        "truehd": CustomRank(enable=False, fetch=True, rank=0),
        "ddplus": CustomRank(enable=False, fetch=True, rank=0),
        "aac": CustomRank(enable=False, fetch=True, rank=70),
        "ac3": CustomRank(enable=False, fetch=True, rank=50),
        "bluray": CustomRank(enable=False, fetch=True, rank=80),
        "webdl": CustomRank(enable=False, fetch=True, rank=90),
        "remux": CustomRank(enable=False, fetch=True, rank=-1000),
        "dvdrip": CustomRank(enable=False, fetch=True, rank=5),
        "bdrip": CustomRank(enable=False, fetch=True, rank=5),
        "brrip": CustomRank(enable=False, fetch=True, rank=0),
        "hdtv": CustomRank(enable=False, fetch=True, rank=0),
        "repack": CustomRank(enable=False, fetch=True, rank=5),
        "proper": CustomRank(enable=False, fetch=True, rank=4),
        "dubbed": CustomRank(enable=False, fetch=True, rank=4),
        "subbed": CustomRank(enable=False, fetch=True, rank=2),
    }

    @model_validator(mode="before")
    def compile_and_validate_patterns(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Compile string patterns to regex.Pattern, keeping compiled patterns unchanged."""
        for field in ("require", "exclude", "preferred"):
            raw_patterns = values.get(field, [])
            compiled_patterns = []
            for pattern in raw_patterns:
                if isinstance(pattern, str):
                    if pattern.startswith("/") and pattern.endswith("/i"):  # case-insensitive
                        compiled_patterns.append(regex.compile(pattern[1:-2], regex.IGNORECASE))
                    elif pattern.startswith("/") and pattern.endswith("/"):  # case-sensitive
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
