"""Unit tests for utility functions."""

import pytest
from datetime import datetime

from gemma_3n.utils.helpers import format_bytes, get_timestamp, slugify, validate_email


class TestHelpers:
    """Test helper utility functions."""
    
    def test_format_bytes(self):
        """Test byte formatting."""
        assert format_bytes(0) == "0.00 B"
        assert format_bytes(1024) == "1.00 KB"
        assert format_bytes(1024 * 1024) == "1.00 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.00 GB"
        assert format_bytes(1536, precision=1) == "1.5 KB"
    
    def test_get_timestamp(self):
        """Test timestamp generation."""
        # Default format
        timestamp = get_timestamp()
        assert timestamp.endswith("Z")
        assert datetime.fromisoformat(timestamp[:-1])  # Remove Z for parsing
        
        # Custom format
        custom_timestamp = get_timestamp("%Y-%m-%d")
        assert len(custom_timestamp) == 10
        assert "-" in custom_timestamp
    
    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert validate_email("user@example.com") is True
        assert validate_email("test.user+tag@domain.co.uk") is True
        assert validate_email("123@test.org") is True
        
        # Invalid emails
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@.com") is False
        assert validate_email("user@domain") is False
    
    def test_slugify(self):
        """Test text slugification."""
        assert slugify("Hello World") == "hello-world"
        assert slugify("Test 123!") == "test-123"
        assert slugify("Multiple   Spaces") == "multiple-spaces"
        assert slugify("Special@#$Characters") == "specialcharacters"
        assert slugify("--Leading-Trailing--") == "leading-trailing"
        assert slugify("UPPERCASE") == "uppercase"