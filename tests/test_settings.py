import pytest
import regex
from pydantic import ValidationError

from RTN.models import CustomRank, DefaultRanking, SettingsModel


@pytest.fixture
def settings():
    return SettingsModel()

@pytest.fixture
def custom_settings():
    return SettingsModel(
        profile="custom",
        require=["/4K/", "/1080p/i"],
        exclude=["CAM|TS|Telesync"],
        preferred=["BluRay", r"/\bS\d+/", "/HDR|HDR10/i"],
        custom_ranks={
            "uhd": CustomRank(enable=True, fetch=True, rank=-200),
            "fhd": CustomRank(enable=True, fetch=True, rank=90),
            "hd": CustomRank(enable=True, fetch=True, rank=60),
            "sd": CustomRank(enable=True, fetch=True, rank=-120),
            "dolby_video": CustomRank(enable=True, fetch=True, rank=-1000),
            "hdr": CustomRank(enable=True, fetch=True, rank=-1000),
            "hdr10": CustomRank(enable=True, fetch=True, rank=-1000),
            "aac": CustomRank(enable=True, fetch=True, rank=70),
            "ac3": CustomRank(enable=True, fetch=True, rank=50),
            "remux": CustomRank(enable=False, fetch=True, rank=-75),
            "webdl": CustomRank(enable=True, fetch=True, rank=90),
            "bluray": CustomRank(enable=True, fetch=True, rank=-90),
        },
    )

@pytest.fixture
def rank_model():
    return DefaultRanking()


class TestSettingsModel:

    # Initialize SettingsModel with default values
    def test_initialize_with_default_values(self, settings):
        assert settings.profile == "default"
        assert settings.require == []
        assert settings.exclude == []
        assert settings.preferred == []
        assert settings.custom_ranks == {
            "uhd": CustomRank(enable=False, fetch=True, rank=120),
            "fhd": CustomRank(enable=False, fetch=True, rank=90),
            "hd": CustomRank(enable=False, fetch=True, rank=80),
            "sd": CustomRank(enable=False, fetch=True, rank=-120),
            "bluray": CustomRank(enable=False, fetch=True, rank=80),
            "hdr": CustomRank(enable=False, fetch=True, rank=40),
            "hdr10": CustomRank(enable=False, fetch=True, rank=50),
            "dolby_video": CustomRank(enable=False, fetch=True, rank=-100),
            "dts_x": CustomRank(enable=False, fetch=True, rank=0),
            "dts_hd": CustomRank(enable=False, fetch=True, rank=0),
            "dts_hd_ma": CustomRank(enable=False, fetch=True, rank=0),
            "atmos": CustomRank(enable=False, fetch=True, rank=0),
            "truehd": CustomRank(enable=False, fetch=True, rank=0),
            "ddplus": CustomRank(enable=False, fetch=True, rank=0),
            "aac": CustomRank(enable=False, fetch=True, rank=70),
            "ac3": CustomRank(enable=False, fetch=True, rank=50),
            "remux": CustomRank(enable=False, fetch=True, rank=-1000),
            "webdl": CustomRank(enable=False, fetch=True, rank=90),
            "repack": CustomRank(enable=False, fetch=True, rank=5),
            "proper": CustomRank(enable=False, fetch=True, rank=4),
            "dubbed": CustomRank(enable=False, fetch=True, rank=4),
            "subbed": CustomRank(enable=False, fetch=True, rank=2),
            "av1": CustomRank(enable=False, fetch=True, rank=0),
        }

    # Initialize SettingsModel with empty values
    def test_initialize_with_empty_values(self):
        settings = SettingsModel(
            profile="",
            require=[],
            exclude=[],
            preferred=[],
            custom_ranks={}
        )
        assert settings.profile == ""
        assert settings.require == []
        assert settings.exclude == []
        assert settings.preferred == []
        assert settings.custom_ranks == {}

    # Verify Custom Settings Initialization
    def test_initialize_with_custom_values(self):
        custom_ranks = {
            "uhd": CustomRank(enable=True, fetch=True, rank=200),
        }
        settings = SettingsModel(
            profile="custom",
            require=["/4K/", "/1080p/i"],
            exclude=["CAM", "TS"],
            preferred=["BluRay", "/HDR10+/i"],
            custom_ranks=custom_ranks
        )
        assert settings.profile == "custom"
        assert settings.custom_ranks["uhd"].rank == 200

    # Test Regex Pattern Compilation
    def test_pattern_compilation(self):
        settings = SettingsModel(
            require=["/4K/", "/1080p/i"],  # "/4K/" is case-sensitive, "/1080p/i" is case-insensitive
            preferred=["/SeNsitive/", "/case insensitive explicit test: 1080p/i"]  # Adjusted for clarity
        )

        # Ensure that each pattern is a compiled regex.Pattern object.
        for pattern in settings.require + settings.preferred:
            assert isinstance(pattern, regex.Pattern)

        test_case = "This is a 4K test"
        assert any(pattern.search(test_case) for pattern in settings.require), "4K case-sensitive match failed" # type: ignore

        test_case = "1080P"
        assert any(pattern.search(test_case) for pattern in settings.require), "1080p case-insensitive match failed" # type: ignore

        test_case = "case sensitive test"
        assert not any(pattern.search(test_case) for pattern in settings.preferred), "Case sensitive match failed" # type: ignore

        test_case = "case insensitive explicit test: 1080p"
        assert any(pattern.search(test_case) for pattern in settings.preferred), "Case insensitive explicit match failed" # type: ignore


    # Test Custom Rank Updates
    def test_custom_rank_updates(self):
        settings = SettingsModel()
        original_rank = settings.custom_ranks["uhd"].rank
        settings.custom_ranks["uhd"].rank = original_rank + 100
        assert settings.custom_ranks["uhd"].rank == original_rank + 100

    # Validate Pattern Matching
    @pytest.mark.parametrize("title,expected_match", [
        ("This is a 4K video", True),
        ("This is a 1080p video", True),
        ("Low Quality CAM", False),
        ("Awesome BluRay Release", True),
        ("Exclusive HDR10+ Content", True),
    ])
    def test_pattern_matching(self, title: str, expected_match: bool):
        settings = SettingsModel(
            require=["/4K/", "/1080p/i"],
            exclude=["CAM|TS|Telesync"],
            preferred=["BluRay", "/HDR10+/i"]
        )
        require_matches = any(pattern.search(title) for pattern in settings.require) # type: ignore
        exclude_matches = any(pattern.search(title) for pattern in settings.exclude) # type: ignore
        preferred_matches = any(pattern.search(title) for pattern in settings.preferred) # type: ignore
        assert expected_match in (require_matches and not exclude_matches, preferred_matches)

    # Error Handling and Validation
    def test_invalid_pattern_type_error(self):
        with pytest.raises(ValidationError):
            SettingsModel(require=["4K", 1080])  # 1080 is not a string or Pattern object # type: ignore
