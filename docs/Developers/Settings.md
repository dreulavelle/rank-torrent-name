## SettingsModel
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L437)
```python 
from RTN.models import SettingsModel
settings = SettingsModel()
```

---
Represents user-defined settings for ranking torrents, including preferences for filtering torrents
based on regex patterns and customizing ranks for specific torrent attributes. This model allows for
advanced customization and fine-grained control over the ranking process.

**Attributes**

* **profile** (str) : Identifier for the settings profile, allowing for multiple configurations.
* **require** (List[str | Pattern]) : Patterns torrents must match to be considered.
* **exclude** (List[str | Pattern]) : Patterns that, if matched, result in torrent exclusion.
* **preferred** (List[str | Pattern]) : Patterns indicating preferred attributes in torrents. Given +5000 points by default.
* **custom_ranks** (Dict[str, Dict[str, CustomRank]]) : Custom ranking configurations for specific attributes, allowing users to define how different torrent qualities and features affect the overall rank.

---

Methods:

    __getitem__(item: str) -> CustomRank: Access custom rank settings via attribute keys.


**Note**

- The `profile` attribute allows users to define multiple settings profiles for different use cases.
- The `require`, `exclude`, and `preferred` attributes are optional!
- The `custom_ranks` attribute contains default values for common torrent attributes, which can be customized by users.
- Patterns enclosed in '/' without a trailing 'i' are compiled as case-sensitive.
- Patterns not enclosed are compiled as case-insensitive by default.

This model supports advanced regex features, enabling powerful and precise filtering and ranking based on torrent titles and attributes.

----

## CustomRank
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L430)
```python 
CustomRank()
```

Custom Ranks used in SettingsModel.

---

### SettingsModel

`SettingsModel` is designed to be fully customizable by __users__, allowing you to define your own filtering criteria, including patterns to require, exclude, and prefer in torrent names. This model empowers you to dynamically configure torrent selection based on your specific patterns and preferences.

Key functionalities:

- **Filtering Torrents:** You have the control to determine which torrents to consider or ignore based on your matching patterns.
- **Prioritizing Torrents:** Indicate your preferred attributes to give certain torrents higher precedence according to your needs.
- **Custom Ranks Usage:** Decide how specific attributes influence the overall ranking, enabling or disabling custom ranks as you see fit.

!!! warning 
    The `SettingsModel` is only used when ranking torrents, you do not need it if you are just wanting to `parse()` torrents.

## Setup your Settings Model

Begin by defining your preferences in a `SettingsModel`. This includes specifying the required patterns, exclusions, preferences, and custom ranks for various torrent attributes. The `SettingsModel` allows you to customize how torrents are filtered and ranked based on your specific needs.

- **require:** These are patterns that must be present in the torrent name for it to be considered.
- **exclude:** These are patterns that, if present in the torrent name, will exclude the torrent from consideration.
- **preferred:** These are patterns that, if present, will give the torrent a higher priority.
- **resolutions:** These will be used to determine what is fetched when ranking torrents.
- **options:** These are options that can be used to customize the behavior of the RTN.
- **languages:** These are languages that can be used to customize the behavior of the RTN.
- **custom_ranks:** These allow you to assign specific ranks to various attributes of the torrents, such as quality or resolution.

Here is what the default settings model looks like, including the default values for each attribute:

## Example Usage

```python
from typing import List, Dict
from RTN.models import SettingsModel, CustomRank

settings = SettingsModel(
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
)
```

We cover a lot already, so users are able to add their own custom regex patterns without worrying about the basic patterns.

### Understanding Fetch and Custom Rank

- `fetch`: Determines if RTN should consider a torrent for downloading based on the attribute. True means RTN will fetch torrents matching this criterion.
- `use_custom_rank`: Controls whether the custom rank value is used in the overall ranking calculation. Disabling it reverts to using the ranking model you set instead. This is useful for toggling custom ranks on and off from a users perspective.
- `rank`: Sets the rank at which that item is graded with.
