import pytest

from RTN import parse
from RTN.fetch import (
    check_fetch,
    check_required,
    fetch_resolution,
    language_handler,
    fetch_audio
)
from RTN.models import LanguagesConfig, OptionsConfig, SettingsModel


@pytest.fixture
def settings():
    return SettingsModel()


@pytest.mark.parametrize("raw_title, expected", [
    ("The.Lion.King.2019.1080p.BluRay.x264.DTS-HD.MA.7.1-FGT", True),
    ("Guardians of the Galaxy (2014)", True),
    ("The Great Gatsby 2013 1080p BluRay x264 AAC - Ozlem", True),
    ("Turning.Red.2022.MULTi.DV.HDR.2160p.DSNP.WEB-DL.DDP5.1.x265.(Alerte.Rouge)-BONBON.mkv", False),
    ("The Adam Project 2022 1080p NF WEB-DL DDP 5 1 Atmos DoVi HDR HEVC-SiC mkv", False)
])
def test_check_fetch(settings: SettingsModel, raw_title: str, expected: bool):
    data = parse(raw_title)
    is_fetchable, failed_keys = check_fetch(data, settings)
    assert is_fetchable is expected, f"Expected {expected} for {raw_title}"
    if not expected:
        assert failed_keys, f"Expected no failed keys, got {failed_keys}"


@pytest.mark.parametrize("raw_title, expected, expected_resolution", [
    ("The.Witcher.US.S01.INTERNAL.4k.WEB.x264-STRiFE", False, "2160p"),
    ("The.Witcher.US.S01.INTERNAL.2160p.WEB.x264-STRiFE", False, "2160p"),
    ("The.Witcher.US.S01.INTERNAL.1080p.WEB.x264-STRiFE", True, "1080p"),
    ("The.Witcher.US.S01.INTERNAL.720p.WEB.x264-STRiFE", True, "720p"),
    ("The.Witcher.US.S01.INTERNAL.480p.WEB.x264-STRiFE", False, "480p"),
    ("The.Witcher.US.S01.INTERNAL.360p.WEB.x264-STRiFE", False, "360p"),
    ("The.Witcher.US.S01.INTERNAL.WEB.x264-STRiFE", True, "unknown"),
])
def test_fetch_resolution(settings: SettingsModel, raw_title: str, expected: bool, expected_resolution: str):
    data = parse(raw_title)
    failed_keys = set()
    assert data.resolution == expected_resolution, f"Expected {expected_resolution} for {raw_title}"
    fetch_resolution(data, settings, failed_keys)
    if not expected:
        assert "resolution" in next(iter(failed_keys)), f"Expected resolution in failed keys for {raw_title}"
    else:
        assert not failed_keys, f"Expected no failed keys for {raw_title}"


@pytest.mark.parametrize("raw_title, expected, message", [
    # Required
    ("This is a 4k video", True, "4K should match as case-insensitive on required on default behavior"),
    ("This is a 1080P video", True, "/1080p/ should match as case-sensitive on required"),
    ("House MD All Seasons (1-8) 720p Ultra-Compressed", True, "Should match because 'compressed' is case-insensitive"),
    ("House MD All Seasons (1-8) 720p spider", True, "Should match because 'spider' is not case-sensitive and required"),
    ("This is a SpiDER test case", True, "Should match because 'spider' is not case-sensitive and required"),
    # Ignored
    ("Awesome BluRay Release", False, "Should not match because 'awesome' is required as case-sensitive"),
    ("Exclusive HDR10+ Content", False, "Should fail because it's not in the list of required patterns")
])
def test_explicit_check_required(raw_title, expected, message):
    data = parse(raw_title)
    settings = SettingsModel(require=["4K", "/1080P/", "/awesome/", "SPIDER|Traffic|compressed"])
    assert check_required(data, settings) is expected, message


@pytest.mark.parametrize("raw_title, exclude_patterns, expected_error", [
    # Should raise GarbageTorrent
    ("This is a 4k video", ["4K"], True),
    ("This is a BraZil video", ["brazil"], True), 
    ("Low Quality CAM", ["CAM"], True),
    ("Game.of.Thrones.S08E01.1080p.WEB-DL.DDP5.1.H.264-GoT", ["\\d{2}"], True),
    # Should not raise exception
    ("Exclusive HDR10+ Content", [], False),
])
def test_explicit_check_excluded(raw_title, exclude_patterns, expected_error):
    data = parse(raw_title)
    settings = SettingsModel(exclude=exclude_patterns)
    is_fetchable, failed_keys = check_fetch(data, settings, speed_mode=False)
    if expected_error:
        assert not is_fetchable
        assert any('exclude_regex' in key for key in failed_keys), f"Expected 'exclude_regex' in failed keys. Got {failed_keys}"
    else:
        assert is_fetchable


@pytest.mark.parametrize("raw_title, expected, expected_failed_keys", [
    ("The Adam Project 2022 1080p", True, []),
    ("The Adam Project 2022 1080p VOSTFR", False, ["lang_fr"]),
    ("The Adam Project 2022 1080p Spanish", True, [])
])
def test_required_languages(settings: SettingsModel, raw_title: str, expected: bool, expected_failed_keys: list):
    """
    Test to make sure we are keeping required languages properly.
    True means it should be kept, False means it should not be kept.
    """
    settings = SettingsModel(
        options=OptionsConfig(
            remove_unknown_languages=False,
            remove_all_trash=True
        ),
        languages=LanguagesConfig(exclude=["fr"])
    )
    data = parse(raw_title)
    is_fetchable, failed_keys = check_fetch(data, settings)
    assert is_fetchable is expected, f"Expected {expected} for {raw_title}"
    if not expected:
        assert failed_keys == expected_failed_keys, f"Expected failed keys {expected_failed_keys}, got {failed_keys}"


@pytest.mark.parametrize("raw_title, expected", [
    ("The Adam Project 2022 1080p", True),
    ("The Adam Project 2022 1080p Japanese", True),
    ("The Adam Project 2022 1080p English", False),
    ("The Adam Project 2022 1080p Hindi", True),
    ("The Adam Project 2022 1080p VOSTFR", False),
    ("The Adam Project 2022 1080p Spanish", False),
])
def test_populate_langs(settings: SettingsModel, raw_title: str, expected: bool):
    """
    Test to make sure we are excluding languages properly.
    True means it should be excluded, False means it should not be excluded.
    """
    settings = SettingsModel(
        options=OptionsConfig(
            remove_all_trash=True,
            # allow_english_in_languages=False,
            remove_unknown_languages=True
        ),
        languages=LanguagesConfig(exclude=["hi", "ja"], required=["fr"])
    )

    data = parse(raw_title)
    value = language_handler(data, settings, set())
    assert value is expected, f"Expected {expected} for {raw_title}"

@pytest.mark.parametrize("raw_title, expected, expected_audio", [
    ("Oppenheimer.2023.2160p.REMUX.IMAX.Dolby.Vision.And.HDR10.PLUS.ENG.ITA.LATINO.DTS-HD.Master.DDP5.1.DV.x265.mkv", False, ["DTS Lossless", "Dolby Digital Plus"]),
    ("Oppenheimer 2023 Bluray 2160p AV1 HDR10 EN/FR/ES OPUS 5.1-UH", False, ["OPUS"]),
])
def test_fetch_audio(settings: SettingsModel, raw_title: str, expected: bool, expected_audio: list):
    """
    RTN doesn't support PCM or OPUS that PTN parses.
    """
    data = parse(raw_title)
    failed_keys = set()
    assert data.audio == expected_audio, f"Expected {expected_audio} for {raw_title}"
    fetch = fetch_audio(data, settings, failed_keys)
    assert fetch == expected
