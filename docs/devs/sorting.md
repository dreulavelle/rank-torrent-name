# Sorting Torrents with `sort_torrents`

## Overview
The `sort_torrents` function sorts a set of `Torrent` objects by their **resolution** and then by **rank**, returning a dictionary where each torrent's `infohash` serves as the key. Torrents are first categorized into resolution buckets, with higher resolutions receiving higher priority. Within each resolution group, torrents are sorted by rank in descending order. **If a torrent lacks a rank, it is treated as having an unknown rank, and is placed at the bottom of the list**. The function ensures that only valid sets of `Torrent` objects are processed, raising a `TypeError` otherwise. This sorting helps prioritize higher-quality torrents for easier selection.

### sort_torrents
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

## Example Usage

```python
from RTN.extras import sort_torrents

sorted_torrents: Dict[str, Torrent] = sort_torrents(torrents)
```