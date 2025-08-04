"""Unit tests for model functions."""

from firesense.fire_detection.model import FireDescription


class TestModelFunctions:
    """Test model-related functions."""

    def test_fire_description_schema(self):
        """Test FireDescription schema creation."""
        # Test valid creation with different classifications
        desc0 = FireDescription(classification=0)
        assert desc0.classification == 0
        assert desc0.has_flame is False
        assert desc0.has_out_of_control_fire is False

        desc1 = FireDescription(classification=1)
        assert desc1.classification == 1
        assert desc1.has_flame is True
        assert desc1.has_out_of_control_fire is False

        desc3 = FireDescription(classification=3)
        assert desc3.classification == 3
        assert desc3.has_flame is True
        assert desc3.has_out_of_control_fire is True

    def test_fire_description_json(self):
        """Test FireDescription JSON serialization."""
        desc = FireDescription(classification=2)
        json_data = desc.model_dump()

        assert json_data == {"classification": 2}
