## ParsedData
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L32)
```python 
ParsedData()
```
Parsed data model for a torrent title.

---

**Methods:**


### .type
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L85)
```python
.type()
```
Returns the type of the torrent based on its attributes.

---

### .to_dict
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L91)
```python
.to_dict()
```
Returns a json serializable dictionary of the parsed data.

----


## Torrent
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L94)
```python 
Torrent()
```
Represents a torrent with metadata parsed from its title and additional computed properties.

**Attributes**

* The original title of the torrent.
* The SHA-1 hash identifier of the torrent.
* Metadata extracted from the torrent title.
* Indicates whether the torrent meets the criteria for fetching based on user settings.
* The computed ranking score of the torrent based on user-defined preferences.
* The Levenshtein ratio comparing the parsed title and the raw title for similarity.

Methods:
    __hash__: Generates a hash based on the infohash of the torrent for set operations.

**Raises**

* If the title is identified as trash and should be ignored by the scraper.

**Example**

```python

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
```

----

**Methods:**

### .to_dict
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L168)
```python
.to_dict()
```

----

## BaseRankingModel
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L171)
```python 
BaseRankingModel()
```

A base class for ranking models used in the context of media quality and attributes.
The ranking values are used to determine the quality of a media item based on its attributes.

**Note**

- The higher the ranking value, the better the quality of the media item.
- The default ranking values are set to 0, which means that the attribute does not affect the overall rank.
- Users can customize the ranking values based on their preferences and requirements by using inheritance.

----


## DefaultRanking
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L258)
```python 
DefaultRanking()
```
Ranking model preset that covers the most common use cases.

---

## BestRanking
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L338)
```python 
BestRanking()
```
Ranking model preset that covers the highest qualities like 4K HDR.

---

## SettingsModel
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L437)
```python 
SettingsModel()
```

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

---
This model supports advanced regex features, enabling powerful and precise filtering and ranking based on torrent titles and attributes.


**Example**


```python

>>> print([pattern.pattern for pattern in settings.require])
['\b4K|1080p\b', '720p']
>>> print([pattern.pattern for pattern in settings.preferred])
['BluRay', '\bS\d+', 'HDR|HDR10']
>>> print(settings.custom_ranks["uhd"].rank)
150
```

----


## CustomRank
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/models.py/#L430)
```python 
CustomRank()
```

Custom Ranks used in SettingsModel.
