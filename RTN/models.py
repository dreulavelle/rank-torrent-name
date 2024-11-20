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

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeAlias, Union

import regex
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from regex import Pattern

from RTN.exceptions import GarbageTorrent


class ParsedData(BaseModel):
    """Parsed data model for a torrent title."""

    raw_title: str
    parsed_title: str = ""
    normalized_title: str = ""
    trash: bool = False
    adult: bool = False
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
    scene: bool = False

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
    trackers: Optional[List[str]] = []
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
    scene: int = 0

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
    scene: int = 2000

    # trash
    cam: int = -10000
    clean_audio: int = -10000
    r5: int = -10000
    satrip: int = -10000
    screener: int = -10000
    size: int = -10000
    telecine: int = -10000
    telesync: int = -10000
    adult: int = -10000


class BestRanking(BaseRankingModel):
    """Ranking model preset that covers the highest qualities like 4K HDR."""

    # quality
    av1: int = 500
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
    dolby_vision: int = 3000
    hdr: int = 2000
    hdr10plus: int = 2100
    sdr: int = 0

    # audio
    aac: int = 100
    ac3: int = 50
    atmos: int = 1000
    dolby_digital: int = 0
    dolby_digital_plus: int = 0
    dts_lossy: int = 100
    dts_lossless: int = 2000
    eac3: int = 150
    flac: int = 0
    mono: int = -1000
    mp3: int = -1000
    stereo: int = 0
    surround: int = 0
    truehd: int = 2000

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


class ConfigModelBase(BaseModel):
    """Base class for config models that need dict-like behavior"""
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default


class ResolutionConfig(ConfigModelBase):
    """Configuration for which resolutions are enabled."""
    def __getitem__(self, key: str) -> Any:
        # Special handling for resolution fields - add 'r' prefix
        field_name = f"r{key}" if key.endswith('p') else key
        return getattr(self, field_name)

    r2160p: bool = Field(default=False)
    r1080p: bool = Field(default=True)
    r720p: bool = Field(default=True)
    r480p: bool = Field(default=False)
    r360p: bool = Field(default=False)
    unknown: bool = Field(default=True)

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: field_name[1:] if field_name.startswith('r') and field_name.endswith('p') else field_name
    )


class OptionsConfig(ConfigModelBase):
    """Configuration for various options."""
    title_similarity: float = Field(default=0.85)
    remove_all_trash: bool = Field(default=True)
    remove_ranks_under: int = Field(default=-10000)
    remove_unknown_languages: bool = Field(default=False)
    allow_english_in_languages: bool = Field(default=False)
    enable_fetch_speed_mode: bool = Field(default=True)
    remove_adult_content: bool = Field(default=True)


class LanguagesConfig(ConfigModelBase):
    """Configuration for which languages are enabled."""
    required: List[str] = Field(default_factory=list)
    exclude: List[str] = Field(default=["ar", "hi", "fr", "es", "de", "ru", "pt", "it"])
    preferred: List[str] = Field(default_factory=list)


class CustomRank(BaseModel):
    """Custom Ranks used in SettingsModel."""
    fetch: bool = Field(default=True)
    use_custom_rank: bool = Field(default=False)
    rank: int = Field(default=0)


class QualityRankModel(ConfigModelBase):
    """Ranking configuration for quality attributes."""
    av1: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    avc: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    bluray: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    dvd: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    hdtv: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    hevc: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    mpeg: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    remux: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    vhs: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    web: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    webdl: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    webmux: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    xvid: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))


class RipsRankModel(ConfigModelBase):
    """Ranking configuration for rips attributes."""
    bdrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    brrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    dvdrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    hdrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    ppvrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    satrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    tvrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    uhdrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    vhsrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    webdlrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    webrip: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))


class HdrRankModel(ConfigModelBase):
    """Ranking configuration for HDR attributes."""
    def __getitem__(self, key: str) -> Any:
        # Special handling for '10bit' key
        if key == '10bit':
            return self.bit10
        return super().__getitem__(key)

    bit10: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    dolby_vision: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    hdr: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    hdr10plus: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    sdr: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))


class AudioRankModel(ConfigModelBase):
    """Ranking configuration for audio attributes."""
    aac: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    ac3: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    atmos: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    dolby_digital: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    dolby_digital_plus: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    dts_lossy: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    dts_lossless: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    eac3: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    flac: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    mono: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    mp3: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    stereo: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    surround: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    truehd: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))


class ExtrasRankModel(ConfigModelBase):
    """Ranking configuration for extras attributes."""
    three_d: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False), alias="3d")
    converted: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    documentary: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    dubbed: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    edition: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    hardcoded: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    network: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    proper: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    repack: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    retail: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    site: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    subbed: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))
    upscaled: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    scene: CustomRank = Field(default_factory=lambda: CustomRank(fetch=True))

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: "3d" if field_name == "three_d" else field_name
    )


class TrashRankModel(ConfigModelBase):
    """Ranking configuration for trash attributes."""
    cam: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    clean_audio: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    pdtv: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    r5: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    screener: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    size: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    telecine: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))
    telesync: CustomRank = Field(default_factory=lambda: CustomRank(fetch=False))


class CustomRanksConfig(ConfigModelBase):
    """Configuration for custom ranks."""
    quality: QualityRankModel = Field(default_factory=QualityRankModel)
    rips: RipsRankModel = Field(default_factory=RipsRankModel)
    hdr: HdrRankModel = Field(default_factory=HdrRankModel)
    audio: AudioRankModel = Field(default_factory=AudioRankModel)
    extras: ExtrasRankModel = Field(default_factory=ExtrasRankModel)
    trash: TrashRankModel = Field(default_factory=TrashRankModel)


PatternType: TypeAlias = Union[Pattern, str]
ProfileType: TypeAlias = str
CustomRankDict: TypeAlias = Dict[str, CustomRank]


class SettingsModel(BaseModel):
    """
    Represents user-defined settings for ranking torrents, including preferences for filtering torrents
    based on regex patterns and customizing ranks for specific torrent attributes.

    Attributes:
        profile (str): Identifier for the settings profile, allowing for multiple configurations.
        require (List[str | Pattern]): Patterns torrents must match to be considered.
        exclude (List[str | Pattern]): Patterns that, if matched, result in torrent exclusion.
        preferred (List[str | Pattern]): Patterns indicating preferred attributes in torrents. Given +10000 points by default.
        resolutions (ResolutionConfig): Configuration for which resolutions are enabled.
        options (OptionsConfig): Configuration for various options like title similarity and trash removal.
        languages (LanguagesConfig): Configuration for which languages are enabled, excluded, and preferred.
        custom_ranks (CustomRanksConfig): Custom ranking configurations for specific attributes.

    Methods:
        compile_and_validate_patterns: Compiles string patterns to regex.Pattern objects, handling case sensitivity.

    Note:
        - Patterns enclosed in '/' are compiled as case-sensitive.
        - Patterns not enclosed are compiled as case-insensitive by default.
        - The model supports advanced regex features for precise filtering and ranking.

    Example:
        >>> settings = SettingsModel(
        ...     profile="default",
        ...     require=["\\b4K|1080p\\b", "720p"],
        ...     exclude=["CAM", "TS"],
        ...     preferred=["BluRay", r"/\\bS\\d+/", "/HDR|HDR10/"],
        ...     resolutions=ResolutionConfig(r1080p=True, r720p=True),
        ...     options=OptionsConfig(remove_all_trash=True),
        ...     languages=LanguagesConfig(required=["en"]),
        ...     custom_ranks=CustomRanksConfig()
        ... )
        >>> print([p.pattern for p in settings.require])
        ['\\b4K|1080p\\b', '720p']
        >>> print(settings.resolutions.r1080p)
        True
        >>> print(settings.options.remove_all_trash)
        True
    """
    profile: ProfileType = Field(
        default="default",
        description="Identifier for the settings profile"
    )
    require: List[PatternType] = Field(
        default_factory=list,
        description="Patterns torrents must match to be considered"
    )
    exclude: List[PatternType] = Field(
        default_factory=list,
        description="Patterns that, if matched, result in torrent exclusion"
    )
    preferred: List[PatternType] = Field(
        default_factory=list,
        description="Patterns indicating preferred attributes in torrents"
    )
    resolutions: ResolutionConfig = Field(
        default_factory=ResolutionConfig,
        description="Configuration for enabled resolutions"
    )
    options: OptionsConfig = Field(
        default_factory=OptionsConfig,
        description="General options for torrent filtering and ranking"
    )
    languages: LanguagesConfig = Field(
        default_factory=LanguagesConfig,
        description="Language preferences and restrictions"
    )
    custom_ranks: CustomRanksConfig = Field(
        default_factory=CustomRanksConfig,
        description="Custom ranking configurations for specific attributes"
    )

    @model_validator(mode="before")
    def compile_and_validate_patterns(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Compile string patterns to regex.Pattern, keeping compiled patterns unchanged."""
        
        def compile_pattern(pattern: PatternType) -> Pattern:
            """Helper function to compile a single pattern."""
            if isinstance(pattern, str):
                if pattern.startswith("/") and pattern.endswith("/"):  # case-sensitive
                    return regex.compile(pattern[1:-1])
                return regex.compile(pattern, regex.IGNORECASE)  # case-insensitive
            elif isinstance(pattern, Pattern):
                return pattern  # Keep already compiled patterns as is
            raise ValueError(f"Invalid pattern type: {type(pattern)}")

        for field in ("require", "exclude", "preferred"):
            if field not in values or values[field] is None:
                values[field] = []
            elif isinstance(values[field], (list, tuple)):
                values[field] = [compile_pattern(p) for p in values[field]]
        
        return values

    @field_validator('profile')
    def validate_profile(cls, v: str) -> str:
        """Validate profile field and default to 'custom' if not a standard profile"""
        if v not in ('default', 'best', 'custom'):
            return 'custom'
        return v

    def __getitem__(self, item: str) -> CustomRankDict:
        """Access custom rank settings via attribute keys."""
        return self.custom_ranks[item]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={
            Pattern: lambda v: f"/{v.pattern}/" if not v.flags & regex.IGNORECASE else v.pattern
        }
    )

    def save(self, path: Union[str, Path]) -> None:
        """
        Save settings to a JSON file.

        Args:
            path: Path where the settings file should be saved.
                 Can be either a string or Path object.

        Example:
            >>> settings = SettingsModel()
            >>> settings.save("my_settings.json")
            >>> settings.save(Path("configs/my_settings.json"))
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with path.open('w', encoding='utf-8') as f:
            json.dump(self.model_dump(mode='json'), f, indent=4)

    @classmethod
    def load(cls, path: Union[str, Path]) -> 'SettingsModel':
        """
        Load settings from a JSON file.

        Args:
            path: Path to the settings file.

        Returns:
            SettingsModel: A new settings instance with the loaded configuration.

        Raises:
            FileNotFoundError: If the settings file doesn't exist.
            JSONDecodeError: If the settings file is corrupted or contains invalid JSON.
            ValidationError: If the settings file contains invalid configuration.
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Settings file not found: {path}")
            
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
            
        return cls.model_validate(data)

    @classmethod
    def load_or_default(cls, path: Optional[Union[str, Path]] = None) -> 'SettingsModel':
        """
        Load settings from a file if it exists, otherwise create default settings and save them.

        Args:
            path: Optional path to the settings file.
                If None, returns default settings without saving.

        Returns:
            SettingsModel: Either the loaded settings or default settings.

        Raises:
            JSONDecodeError: If the settings file is corrupted or contains invalid JSON.
        """
        if path is None:
            return cls()
            
        path = Path(path)
        try:
            return cls.load(path)
        except FileNotFoundError:
            settings = cls()
            settings.save(path)
            return settings
