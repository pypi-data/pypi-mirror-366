"""Unit tests for video processing functions."""

import pytest

from firesense.fire_detection.video import validate_video_id


class TestVideoFunctions:
    """Test video processing functions."""

    def test_validate_video_id_clean(self):
        """Test video ID validation with clean ID."""
        video_id = "dQw4w9WgXcQ"
        result = validate_video_id(video_id)
        assert result == video_id

    def test_validate_video_id_from_url(self):
        """Test video ID extraction from YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share"
        result = validate_video_id(url)
        assert result == "dQw4w9WgXcQ"

    def test_validate_video_id_from_short_url(self):
        """Test video ID extraction from short YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ?t=30"
        result = validate_video_id(url)
        assert result == "dQw4w9WgXcQ"

    def test_validate_video_id_invalid(self):
        """Test invalid video ID raises error."""
        with pytest.raises(ValueError, match="Invalid YouTube video ID"):
            validate_video_id("invalid")
