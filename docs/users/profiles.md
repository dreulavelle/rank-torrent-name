# Profiles

Profiles are used to configure the behavior of RTN. They are used to set the default ranking model, the minimum score a torrent must have to be included in the results, and the maximum number of torrents to return.

We have 3 profiles built in that are named `default`, `best`, and `custom`. The `custom` profile has all values set to 0, providing a neutral starting point for user customization.

---

## Quality

| Attribute | Default | Best | Custom |
|:----------|--------:|-----:|-------:|
| av1 | 0 | 0 | 0 |
| avc | 500 | 500 | 0 |
| bluray | 100 | 100 | 0 |
| dvd | -1000 | -5000 | 0 |
| hdtv | -1000 | -5000 | 0 |
| hevc | 500 | 500 | 0 |
| mpeg | -100 | -1000 | 0 |
| remux | -10000 | 10000 | 0 |
| vhs | -10000 | -10000 | 0 |
| web | 150 | 100 | 0 |
| webdl | 5000 | 200 | 0 |
| webmux | -10000 | -10000 | 0 |
| xvid | -10000 | -10000 | 0 |
| pdtv | -10000 | -10000 | 0 |

---

## Rips

| Attribute | Default | Best | Custom |
|:----------|--------:|-----:|-------:|
| bdrip | -1000 | -5000 | 0 |
| brrip | -1000 | -10000 | 0 |
| dvdrip | -1000 | -5000 | 0 |
| hdrip | -1000 | -10000 | 0 |
| ppvrip | -1000 | -10000 | 0 |
| tvrip | -10000 | -10000 | 0 |
| uhdrip | -1000 | -5000 | 0 |
| vhsrip | -10000 | -10000 | 0 |
| webdlrip | -10000 | -10000 | 0 |
| webrip | 30 | -1000 | 0 |

---

## HDR

| Attribute | Default | Best | Custom |
|:----------|--------:|-----:|-------:|
| bit_10 | 5 | 100 | 0 |
| dolby_vision | 50 | 1000 | 0 |
| hdr | 50 | 500 | 0 |
| hdr10plus | 0 | 1000 | 0 |
| sdr | 0 | 0 | 0 |

---

## Audio

| Attribute | Default | Best | Custom |
|:----------|--------:|-----:|-------:|
| aac | 250 | 100 | 0 |
| ac3 | 30 | 50 | 0 |
| atmos | 400 | 1000 | 0 |
| dolby_digital | 0 | 0 | 0 |
| dolby_digital_plus | 0 | 0 | 0 |
| dts_lossy | 600 | 100 | 0 |
| dts_lossless | 0 | 1000 | 0 |
| eac3 | 250 | 150 | 0 |
| flac | 0 | 0 | 0 |
| mono | -10000 | -1000 | 0 |
| mp3 | -10000 | -1000 | 0 |
| stereo | 0 | 0 | 0 |
| surround | 0 | 0 | 0 |
| truehd | -100 | 1000 | 0 |

---

## Extras

| Attribute | Default | Best | Custom |
|:----------|--------:|-----:|-------:|
| three_d | -10000 | -10000 | 0 |
| converted | -1250 | -1000 | 0 |
| documentary | -250 | -250 | 0 |
| dubbed | 0 | -1000 | 0 |
| edition | 100 | 100 | 0 |
| hardcoded | 0 | 0 | 0 |
| network | 300 | 0 | 0 |
| proper | 1000 | 20 | 0 |
| repack | 1000 | 20 | 0 |
| retail | 0 | 0 | 0 |
| site | -10000 | -10000 | 0 |
| subbed | 0 | 0 | 0 |
| upscaled | -10000 | -10000 | 0 |

---

## Trash

| Attribute | Default | Best | Custom |
|:----------|--------:|-----:|-------:|
| cam | -10000 | -10000 | 0 |
| clean_audio | -10000 | -10000 | 0 |
| r5 | -10000 | -10000 | 0 |
| satrip | -10000 | -10000 | 0 |
| screener | -10000 | -10000 | 0 |
| size | -10000 | -10000 | 0 |
| telecine | -10000 | -10000 | 0 |
| telesync | -10000 | -10000 | 0 |

---

## Custom Profiles

These are just presets that you can use as a starting point to create your own custom profiles. To edit the ranks, you can simply enable `use_custom_rank` in the settings and edit the `rank` as you see fit.