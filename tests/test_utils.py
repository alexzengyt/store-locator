import pytest
from app.utils import calculate_bounding_box, calculate_distance_miles

class TestUtils:
    def test_bounding_box_returns_four_keys(self):
        result = calculate_bounding_box(42.3601, -71.0589, 10)
        assert "min_lat" in result
        assert "max_lat" in result
        assert "min_lon" in result
        assert "max_lon" in result

    def test_bounding_box_correct_range(self):
        result = calculate_bounding_box(42.3601, -71.0589, 10)
        assert result["min_lat"] < 42.3601 < result["max_lat"]
        assert result["min_lon"] < -71.0589 < result["max_lon"]

    def test_distance_same_point(self):
        result = calculate_distance_miles(42.3601, -71.0589, 42.3601, -71.0589)
        assert result == 0.0

    def test_distance_known_points(self):
        result = calculate_distance_miles(42.3601, -71.0589, 42.3555, -71.0602)
        assert result < 1.0