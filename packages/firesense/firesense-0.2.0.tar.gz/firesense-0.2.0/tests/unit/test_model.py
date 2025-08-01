"""Unit tests for model functions."""

import pytest
from gemma_3n.fire_detection.model import FireDescription


class TestModelFunctions:
    """Test model-related functions."""
    
    def test_fire_description_schema(self):
        """Test FireDescription schema creation."""
        # Test valid creation
        desc = FireDescription(has_flame=True, has_out_of_control_fire=False)
        assert desc.has_flame is True
        assert desc.has_out_of_control_fire is False
        
    def test_fire_description_json(self):
        """Test FireDescription JSON serialization."""
        desc = FireDescription(has_flame=False, has_out_of_control_fire=True)
        json_data = desc.model_dump()
        
        assert json_data == {
            "has_flame": False,
            "has_out_of_control_fire": True
        }