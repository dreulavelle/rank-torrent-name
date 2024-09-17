## Parsing Overview

The RTN package offers comprehensive and powerful functionality for parsing torrent titles and extracting detailed metadata. This functionality is primarily implemented through two key components: the `parse` function in `parser.py` and the `ParsedData` model in `models.py`. In this section, we will provide an in-depth look at these components and their roles in the parsing process.

### parser.py

The `parser.py` module is the core of the parsing functionality. It is responsible for analyzing torrent titles and enriching them with additional metadata. This module includes the crucial `parse` function that works to achieve this goal.

## ParsedData Model

The `ParsedData` model is a comprehensive data structure that represents the parsed metadata of a torrent title. It uses Pydantic's `BaseModel` for data validation and serialization.

### Attributes

| Attribute         | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `raw_title`       | The original, unprocessed torrent title.                                    |
| `parsed_title`    | The cleaned and standardized version of the title.                          |
| `normalized_title`| A further normalized version of the title for easier matching and comparison.|
| `trash`           | Indicates if the torrent is considered trash.                               |
| `year`            | The release year of the content (if available).                             |
| `resolution`      | The video resolution (e.g., "1080p", "4K").                                 |
| `seasons`         | List of season numbers for TV shows.                                        |
| `episodes`        | List of episode numbers for TV shows.                                       |
| `complete`        | Indicates if the torrent contains a complete season or series.              |
| `volumes`         | List of volume numbers.                                                     |
| `languages`       | List of languages available in the torrent.                                 |
| `quality`         | The overall quality descriptor (e.g., "HDTV", "WEBRip").                    |
| `hdr`             | List of HDR formats.                                                        |
| `codec`           | The video codec used (e.g., "HEVC").                                |
| `audio`           | List of audio codecs or formats.                                            |
| `channels`        | List of audio channels.                                                     |
| `dubbed`          | Indicates if the torrent is dubbed.                                         |
| `subbed`          | Indicates if the torrent has subtitles.                                     |
| `date`            | The release date of the torrent.                                            |
| `group`           | The release group responsible for the torrent.                              |
| `edition`         | The edition of the torrent.                                                 |
| `bit_depth`       | The bit depth of the video.                                                 |
| `bitrate`         | The bitrate of the video.                                                   |
| `network`         | The network that aired the content.                                         |
| `extended`        | Indicates if the torrent is an extended version.                            |
| `converted`       | Indicates if the torrent has been converted from another format.            |
| `hardcoded`       | Indicates if the torrent has hardcoded subtitles.                           |
| `region`          | The region code of the torrent.                                             |
| `ppv`             | Indicates if the torrent is a pay-per-view content.                         |
| `_3d`             | Indicates if the torrent is in 3D.                                          |
| `site`            | The site from which the torrent was sourced.                                |
| `size`            | The size of the torrent.                                                    |
| `proper`          | Indicates if the torrent is a proper release.                               |
| `repack`          | Indicates if the torrent is a repack.                                       |
| `retail`          | Indicates if the torrent is a retail version.                               |
| `upscaled`        | Indicates if the torrent has been upscaled.                                 |
| `remastered`      | Indicates if the torrent has been remastered.                               |
| `unrated`         | Indicates if the torrent is an unrated version.                             |
| `documentary`     | Indicates if the torrent is a documentary.                                  |
| `episode_code`    | The episode code of the torrent.                                            |
| `country`         | The country of origin of the content.                                       |
| `container`       | The container format of the torrent.                                        |
| `extension`       | The file extension of the torrent.                                          |
| `torrent`         | Indicates if the data represents a torrent.                                 |

##### Usage Examples

1. Creating a ParsedData instance:

```python
from RTN.models import ParsedData

parsed_data = parse("Game.of.Thrones.S01E01.1080p.WEBRip.DD5.1.x264-GalaxyRG[TGx]")
print(result)
```

Result:
```python
ParsedData(
    raw_title='Game.of.Thrones.S01E01.1080p.WEBRip.DD5.1.x264-GalaxyRG[TGx]',
    parsed_title='Game of Thrones',
    normalized_title='game of thrones',
    trash=False,
    resolution='1080p',
    seasons=[1],
    episodes=[1],
    quality='WEBRip',
    codec='avc',
    audio=['Dolby Digital'],
    channels=['5.1'],
    group='GalaxyRG',
)
```



2. Accessing attributes:

```python
print(parsed_data.resolution)  # Output: "1080p"
print(parsed_data.type)  # Output: "show"
```

3. Converting to json:

```python
data_dict = parsed_data.to_dict()
print(data_dict)
# Output: JSON string representation of the ParsedData instance
```

##### Benefits for Developers

- **Standardization**: The `ParsedData` model ensures consistent representation of parsed torrent metadata across the application.
- **Type Safety**: Pydantic's type checking helps catch errors early in development.
- **Easy Serialization**: The `to_dict()` method allows for simple conversion to JSON for API responses or database storage.
- **Extensibility**: New attributes can be easily added to accommodate future parsing requirements.

By using the `ParsedData` model, developers can work with structured, validated torrent metadata, making it easier to implement features like searching, filtering, and ranking of torrents based on their attributes.
