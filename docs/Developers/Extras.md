# Extras

## Torrent Parser

You can also parse a torrent title similar to how PTN works. This is an enhanced version of PTN that combines RTN's parsing as well. This also includes enhanced episode parsing as well that covers a much better range of titles.

Using the example above:

```py
from RTN import parse
parsed = parse("Example.Movie.2020.1080p.BluRay.x264-Example")

print(parsed.data.raw_title)    # Output: "Example.Movie.2020.1080p.BluRay.x264-Example"
print(parsed.data.parsed_title) # Output: "Example Movie"
print(parsed.data.year)         # Output: [2020]
```

## Checking Title Similarity

Sometimes, you might just want to check if two titles match closely enough, without going through the entire ranking process. RTN provides a simple function, title_match, for this purpose:

```py
from RTN import title_match

# Check if two titles are similar above a threshold of 0.9
match = title_match("Correct Movie Title 2020", "Correct Movie Title (2020)")
print(match)  # Output: True if similarity is above 0.9, otherwise False
>>> True
```

This functionality is especially useful when you have a list of potential titles and want to find the best match for a given reference title.

## Trash Check

Maybe you just want to use our own garbage collector to weed out bad titles in your current scraping setup?

```py
from RTN import check_trash

if check_trash(raw_title):
    # You can safely remove any title or item from being scraped if this returns True!
    ...
```

## Movie Check

Now you can check if a raw torrent title is a `movie` or a `show` type!

```py
from RTN.parser import get_type, parse

parsed_data = parse("Joker.2019.PROPER.mHD.10Bits.1080p.BluRay.DD5.1.x265-TMd", remove_trash = False)
print(parsed_data.type)
>>> "movie"
```
