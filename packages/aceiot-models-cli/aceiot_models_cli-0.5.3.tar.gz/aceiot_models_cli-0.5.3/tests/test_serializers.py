"""Pytest-compatible tests for all serializers in aceiot-models."""

from .test_serializers_core import (
    run_all_serializer_tests,
)
from .test_serializers_core import (
    test_agent_config_serialization as _test_agent_config_serialization,
)
from .test_serializers_core import (
    test_api_response_serializer as _test_api_response_serializer,
)
from .test_serializers_core import (
    test_auto_detect_model_type as _test_auto_detect_model_type,
)
from .test_serializers_core import (
    test_bulk_serializer as _test_bulk_serializer,
)
from .test_serializers_core import (
    test_datetime_serializer as _test_datetime_serializer,
)
from .test_serializers_core import (
    test_deserialize_from_api as _test_deserialize_from_api,
)
from .test_serializers_core import (
    test_error_handling as _test_error_handling,
)
from .test_serializers_core import (
    test_hash_serializer as _test_hash_serializer,
)
from .test_serializers_core import (
    test_hawke_config_serialization as _test_hawke_config_serialization,
)
from .test_serializers_core import (
    test_model_serializer_basic as _test_model_serializer_basic,
)
from .test_serializers_core import (
    test_model_serializer_complex as _test_model_serializer_complex,
)
from .test_serializers_core import (
    test_serialize_for_api as _test_serialize_for_api,
)
from .test_serializers_core import (
    test_timeseries_serialization as _test_timeseries_serialization,
)
from .test_serializers_core import (
    test_validation_serializer as _test_validation_serializer,
)
from .test_serializers_core import (
    test_weather_data_serialization as _test_weather_data_serialization,
)


def test_model_serializer_basic() -> None:
    """Test basic ModelSerializer functionality."""
    result = _test_model_serializer_basic()
    assert result["passed"], f"Test failed: {result['error']}"


def test_model_serializer_complex() -> None:
    """Test ModelSerializer with complex nested models."""
    result = _test_model_serializer_complex()
    assert result["passed"], f"Test failed: {result['error']}"


def test_bulk_serializer() -> None:
    """Test BulkSerializer functionality."""
    result = _test_bulk_serializer()
    assert result["passed"], f"Test failed: {result['error']}"


def test_hash_serializer() -> None:
    """Test HashSerializer functionality."""
    result = _test_hash_serializer()
    assert result["passed"], f"Test failed: {result['error']}"


def test_datetime_serializer() -> None:
    """Test DateTimeSerializer functionality."""
    result = _test_datetime_serializer()
    assert result["passed"], f"Test failed: {result['error']}"


def test_validation_serializer() -> None:
    """Test ValidationSerializer functionality."""
    result = _test_validation_serializer()
    assert result["passed"], f"Test failed: {result['error']}"


def test_api_response_serializer() -> None:
    """Test APIResponseSerializer functionality."""
    result = _test_api_response_serializer()
    assert result["passed"], f"Test failed: {result['error']}"


def test_auto_detect_model_type() -> None:
    """Test auto_detect_model_type functionality."""
    result = _test_auto_detect_model_type()
    assert result["passed"], f"Test failed: {result['error']}"


def test_serialize_for_api() -> None:
    """Test serialize_for_api functionality."""
    result = _test_serialize_for_api()
    assert result["passed"], f"Test failed: {result['error']}"


def test_deserialize_from_api() -> None:
    """Test deserialize_from_api functionality."""
    result = _test_deserialize_from_api()
    assert result["passed"], f"Test failed: {result['error']}"


def test_timeseries_serialization() -> None:
    """Test serialization of timeseries data."""
    result = _test_timeseries_serialization()
    assert result["passed"], f"Test failed: {result['error']}"


def test_weather_data_serialization() -> None:
    """Test serialization of weather data."""
    result = _test_weather_data_serialization()
    assert result["passed"], f"Test failed: {result['error']}"


def test_hawke_config_serialization() -> None:
    """Test serialization of Hawke configurations."""
    result = _test_hawke_config_serialization()
    assert result["passed"], f"Test failed: {result['error']}"


def test_agent_config_serialization() -> None:
    """Test serialization of agent configurations."""
    result = _test_agent_config_serialization()
    assert result["passed"], f"Test failed: {result['error']}"


def test_error_handling() -> None:
    """Test error handling in serializers."""
    result = _test_error_handling()
    assert result["passed"], f"Test failed: {result['error']}"


# Export run_all_serializer_tests for CLI usage
__all__ = ["run_all_serializer_tests"]
