# Frequently Asked Questions

## 🚀 Quick Start
- Set `require` and `exclude` patterns to filter torrents
- Adjust `resolutions` and `languages` to match your preferences
- Fine-tune with `custom_ranks` for advanced control

---

## 🔍 Filtering Settings

#### How do I use the "require", "exclude", and "preferred" settings?
A: These settings allow you to specify patterns (using simple strings or regular expressions) to filter and prioritize torrents:

1. **require**: Patterns that must be present in a torrent name for it to be considered.

    ```
    require = ["1080p", "\\b202[0-3]\\b"]
    ```

    This would only consider 1080p content with a year between 2020 and 2023.

2. **exclude**: Patterns that, if present, will cause a torrent to be ignored.

    ```
    exclude = ["CAM", "LQ|LOW.?QUALITY"]
    ```

    This would exclude CAM releases and those with "LQ" or "LOW QUALITY" in the name.

    !!! note "This is one example but **CAM** releases are already parsed out by default, so this won't be needed."

3. **preferred**: Patterns that, if present, will give a torrent higher priority in ranking.

    ```
    preferred = ["BluRay", "SPARKS|AMIABLE|GECKOS"]
    ```

    This would prefer BluRay releases and those from specific groups `SPARKS`, `AMIABLE` or `GECKOS`.

All these settings support both simple string matching and more complex regular expressions, allowing for flexible and powerful torrent filtering and prioritization.

---

## 🎬 Resolution Settings

#### How do I control which resolutions are accepted?
A: The "**resolutions**" setting allows you to specify which resolutions you want to accept. Set the value to True for resolutions you want to include, and False for those you want to exclude.

#### How does sorting work for resolutions?
A: Torrents are sorted into resolution buckets, with higher resolutions given higher priority. The order of priority is typically:

1. 2160p (4K)
2. 1080p
3. 720p
4. 480p
5. 360p
6. Unknown resolution

Within each resolution bucket, torrents are then sorted by their rank in descending order. This means that for each resolution category, the highest-ranked torrents appear first. If a torrent doesn't have a rank, it's treated as having an unknown rank and placed at the bottom of its resolution group.

This sorting method ensures that you get the best quality options within your preferred resolution ranges, making it easier to select the most suitable torrent for your needs.

---

## 🌐 Language Settings

#### How do I set my language preferences?
A: The "**languages**" setting has three sub-settings:
- `required`: List 2-character language codes that must be present.
- `exclude`: List 2-character language codes you don't want.
- `preferred`: List 2-character language codes you prefer.

Example: `["es", "de", "fr", "ja"]`

There is a few preset language codes you can use as well:
  - `any`: This will include all languages.
  - `common`: This will include common languages like English, Spanish, French, Japanese, etc.
  - `anime`: This will include anime languages. (`ja`, `en`, `zh`)
  - `nonanime`: This will include non-anime languages. (`en`, `zh`)

!!! note "All language preferences use ISO 639-1 two-letter language codes."
!!! tip "If you want to exclude all languages, regardless of language preferences, set this to `["any"]`"

---

## ⚙️ Options Settings

#### What does the "title_similarity" option do?
A: The `title_similarity` option (default 0.85) sets how closely a torrent's title must match the expected title. A higher value (closer to 1.0) requires a more exact match.

!!! note "Titles are normalized to remove special characters and extra whitespace, so a value of `0.85` is quite lenient!"
!!! warning "If you want to include all torrents, regardless of title similarity, set this to `0`, however anything below `0.85` will include terrible results!"

#### What is the "remove_all_trash" option?
A: When set to True, the `remove_all_trash` option (default True) automatically filters out torrents considered low quality or "trash" based on predefined criteria.

This excludes torrents with indicators of poor quality or undesirable sources, such as:

- CAM, TS (TeleSYNC), TC (TeleCINE) releases
- Screener or SCR versions
- Pre-DVD releases
- DVB-Rip and SAT-Rip sources
- R5/R6 releases
- Leaked versions
- Deleted scenes
- HQ audio cleanups

For more information on the trash regex, see [Parsett Trash Regex](https://github.com/dreulavelle/PTT/blob/main/PTT/handlers.py#L60).
These filters help ensure that only higher quality releases are considered, improving the overall quality of your media collection.

#### How does the "remove_ranks_under" option work?
A: The `remove_ranks_under` option (default -10000) sets a minimum rank threshold. Torrents ranked below this value will be excluded from results.

!!! note "Bonus tip! If you want to exclude torrents that don't get ranked or have a negative rank, you can set this to `0`. Ensuring you only get positive ranked torrents in your results."

#### What does "remove_unknown_languages" do?
A: When set to True, the `remove_unknown_languages` option (default False) will exclude torrents that don't have a language in the title.

#### What is the purpose of "allow_english_in_languages"?
A: The `allow_english_in_languages` option (default False), when set to True, allows English language torrents to be included even if a user has excluded English from their language preferences. This can be useful for users who want to prioritize content in specific languages but still want access to English-language releases if they're available alongside their preferred languages. It essentially bypasses the language exclusion for English, ensuring that multilingual torrents containing English aren't filtered out due to strict language settings.

One scenario is if you wanted a movie that's released in Spanish, and you excluded the Spanish language, but you still want to include it if it's in English as well. This setting works great for Anime as well that you want to include if it's in English as well.

---

## 🏆 Custom Ranks

#### How do I use custom ranks?
A: Custom ranks allow you to assign specific values to various attributes of torrents. 

| Setting | Type | Description |
|---------|------|-------------|
| `fetch` | Boolean | Determines if the attribute should be picked or not |
| `use_custom_rank` | Boolean | Enables or disables the use of a custom rank |
| `rank` | Number | Sets the importance of the attribute |

!!! tip "Boolean's are pretty simple, if you want the attribute, set it to `True`, if you don't, set it to `False`"

Ranks are additive, so a higher rank will be prioritized over a lower rank. You can use this to your advantage to fine tune the torrents that are picked up. 

!!! note "How's it work?"
    - If `fetch` is set to `False`, this is equivalent to saying you don't want that attribute in the title.
    - You can set a negative rank to subtract from the overall rank. This is useful if you want to ignore certain torrents. Example: `-100` will be subtracted from the overall rank.
    - Rankings for individual attributes accumulate. If a file matches three attributes with individual rankings of 100, the overall rank of that file will be 300. Then they are sorted by their overall score.

#### Can I prioritize certain audio or video codecs?
A: Yes! In the `custom_ranks` section, you can adjust the rank values for different codecs. Higher rank values will be prioritized.

Remember, these settings allow you to fine-tune RTN to your specific preferences. Don't be afraid to experiment with different configurations to find what works best for you!

#### How high or low can I set the ranks?
A: You have complete flexibility when it comes to setting ranks in RTN. There are no strict upper or lower limits on the rank values you can use. You can set ranks to any integer value, positive or negative, that suits your needs. This allows for a wide range of customization:

- You can use small, single-digit numbers (like 1, 2, 3) for subtle differences.
- You can use larger numbers (like 100, 500, 1000) for more significant distinctions.
- You can even use very large numbers (like 10000, 50000, 100000) if you want extreme prioritization.
- Negative numbers are also valid, allowing you to penalize certain attributes.

The key is to choose a scale that makes sense for your specific use case. For example:

- If you're making fine distinctions, you might use a scale from -10 to +10.
- For broader categories, you might use -1000 to +1000.
- If you want certain attributes to always outweigh others, you might use values in the tens of thousands.

!!! warning "Remember, ranks are additive, so consider how they'll interact when multiple attributes are present. Experiment with different scales to find what works best for your specific needs and preferences."

#### What's the best way to get started with custom ranks?
A: The best way to get started with custom ranks is to look at a few filenames that you would prefer and rank those attributes higher than others. For instance:

1. Identify your preferred qualities: If you want HDR or REMUX versions, you would rank these attributes higher.
2. Assign higher ranks: Give these preferred attributes (like HDR or REMUX) higher rank values compared to lower quality options.
3. Fine-tune: Adjust other attributes based on your preferences, giving lower ranks to less desirable qualities.

**Remember, the goal is to create a ranking system that prioritizes the qualities you value most in your media files.**
