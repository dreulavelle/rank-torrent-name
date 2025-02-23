from pathlib import Path

from RTN.file_parser import parse_media_file

TEST_VIDEO_PATH = Path(__file__).parent / "video" / "[Yameii] Mushoku Tensei - Jobless Reincarnation - S02E15 [English Dub] [CR WEB-DL 1080p] [6CD6B5CA].mkv"


def test_media_file_parser():
    """Test the MediaFileParser class"""
    metadata = parse_media_file(TEST_VIDEO_PATH)
    assert metadata is not None
    assert metadata.bitrate is not None
    assert metadata.audio is not None
    assert metadata.video is not None
    assert metadata.subtitles is not None
    assert metadata.filename is not None
    assert metadata.file_size is not None
    assert metadata.duration is not None
