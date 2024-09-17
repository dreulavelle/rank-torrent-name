## get_lev_ratio
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/extras.py/#L39)
```python
.get_lev_ratio(
   correct_title: str, parsed_title: str, threshold: float = 0.85
)
```

---
Compares two titles using the Levenshtein ratio to determine similarity.


**Args**

* The reference title to compare against.
* The title to compare with the reference title.
* The similarity threshold to consider the titles as matching.


**Returns**

* The Levenshtein ratio between the two titles.


----


## title_match
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/extras.py/#L23)
```python
.title_match(
   correct_title: str, parsed_title: str, threshold: float = 0.85
)
```

---
Compares two titles using the Levenshtein ratio to determine similarity.


**Args**

* The reference title to compare against.
* The title to compare with the reference title.
* The similarity threshold to consider the titles as matching.


**Returns**

* True if the titles match, False otherwise.


----


## sort_torrents
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/extras.py/#L64)
```python
.sort_torrents(
   torrents: Set[Torrent]
)
```

---
Sorts a set of Torrent objects by their resolution bucket and then by their rank in descending order.
Returns a dictionary with infohash as keys and Torrent objects as values.


**Args**

* A set of Torrent objects.


**Raises**

* If the input is not a set of Torrent objects.


**Returns**

* A dictionary of Torrent objects sorted by resolution and rank in descending order,
with the torrent's infohash as the key.

----


## extract_seasons
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/extras.py/#L119)
```python
.extract_seasons(
   raw_title: str
)
```

---
Extract season numbers from the title or filename.


**Args**

* The original title of the torrent to analyze.


**Returns**

* A list of extracted season numbers from the title.


----


## extract_episodes
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/extras.py/#L134)
```python
.extract_episodes(
   raw_title: str
)
```

---
Extract episode numbers from the title or filename.


**Args**

* The original title of the torrent to analyze.


**Returns**

* A list of extracted episode numbers from the title.


----


## episodes_from_season
[source](https://github.com/dreulavelle/rank-torrent-name/blob/main/RTN/extras.py/#L149)
```python
.episodes_from_season(
   raw_title: str, season_num: int
)
```

---
Only return episode numbers if the season number is found in the title
and the season number matches the input season number.


**Args**

* The original title of the torrent to analyze.
* The season number to extract episodes for.


**Returns**

* A list of extracted episode numbers for the specified season.

