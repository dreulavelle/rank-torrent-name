import pytest
import regex
from pydantic import ValidationError

from RTN.models import SettingsModel, DefaultRanking, ResolutionConfig, OptionsConfig


@pytest.fixture
def settings():
    return SettingsModel()

@pytest.fixture
def custom_settings():
    return SettingsModel(
        require=["/4K/", "/1080p/i"],
        exclude=["CAM|TS|Telesync"],
        preferred=["BluRay", r"/\bS\d+/", "/HDR|HDR10/i"]
    )

@pytest.fixture
def rank_model():
    return DefaultRanking()


@pytest.mark.parametrize("title,expected_match", [
    ("This is a 4K video", True),
    ("This is a 1080p video", True),
    ("Low Quality CAM", False),
    ("Awesome BluRay Release", True),
    ("Exclusive HDR10+ Content", True),
])
def test_pattern_matching(title: str, expected_match: bool):
    settings = SettingsModel(
        require=["/4K/", "1080p"],
        exclude=["CAM|TS|Telesync"],
        preferred=["BluRay", "HDR10+"]
    )
    require_matches = any(pattern.search(title) for pattern in settings.require) # type: ignore
    exclude_matches = any(pattern.search(title) for pattern in settings.exclude) # type: ignore
    preferred_matches = any(pattern.search(title) for pattern in settings.preferred) # type: ignore
    assert expected_match in (require_matches and not exclude_matches, preferred_matches)


@pytest.mark.parametrize("require_patterns, should_raise_error, expected_message", [
    (["4K", 1080], True, "1080 is not a string or Pattern object"),  # Invalid pattern type
    ([regex.compile(r"\b4K|1080p\b"), regex.compile(r"720p")], False, "We should support a list of regex Patterns as well."),  # All regex patterns
    ([regex.compile(r"\b4K|1080p\b"), "/720p/"], False, "We should support a list of regex Patterns as well as strings"),  # Mixed regex patterns and strings
])
def test_pattern_handling(require_patterns, should_raise_error, expected_message):
    if should_raise_error:
        with pytest.raises(ValidationError):
            SettingsModel(require=require_patterns)
    else:
        settings = SettingsModel(require=require_patterns)
        assert all(isinstance(pattern, regex.Pattern) for pattern in settings.require), expected_message


def test_changed_only_returns_only_overrides():
    s = SettingsModel(
        name="custom",
        enabled=False,
        require=["/4K/", "1080p"],
        resolutions=ResolutionConfig(r2160p=True),
        options=OptionsConfig(title_similarity=0.9),
    )
    assert s.changed_only() == {
        "name": "custom",
        "enabled": False,
        "require": ["4K", "1080p"],
        "exclude": [],
        "preferred": [],
        "resolutions": {"r2160p": True},
        "options": {"title_similarity": 0.9},
    }
