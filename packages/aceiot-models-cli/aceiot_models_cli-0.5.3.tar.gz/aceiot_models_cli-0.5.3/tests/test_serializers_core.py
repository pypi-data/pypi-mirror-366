"""Core serializer test functions that return test results as dictionaries.

This module contains the original test functions that return dictionaries
for use by the CLI command and test runner.
"""

import base64
import json
from datetime import datetime, timezone
from typing import Any

from aceiot_models import (
    AgentConfigCreate,
    BACnetData,
    ClientCreate,
    DerEventCreate,
    GatewayCreate,
    HawkeConfigCreate,
    PointCreate,
    PointSample,
    SiteCreate,
    TimeseriesData,
    UserCreate,
    VolttronAgentCreate,
    WeatherData,
)
from aceiot_models.serializers import (
    APIResponseSerializer,
    BulkSerializer,
    DateTimeSerializer,
    DeserializationError,
    HashSerializer,
    ModelSerializer,
    SerializationError,
    ValidationSerializer,
    auto_detect_model_type,
    deserialize_from_api,
    serialize_for_api,
)


def test_model_serializer_basic() -> dict[str, Any]:
    """Test basic ModelSerializer functionality."""
    test_name = "ModelSerializer - Basic Operations"
    try:
        # Test with a simple model
        client = ClientCreate(
            name="test-client",
            nice_name="Test Client",
            bus_contact="business@example.com",
            tech_contact="tech@example.com",
            address="123 Test St",
        )

        # Test serialize to dict
        data = ModelSerializer.serialize_to_dict(client)
        assert isinstance(data, dict)
        assert data["name"] == "test-client"
        assert data["nice_name"] == "Test Client"

        # Test serialize to JSON
        json_str = ModelSerializer.serialize_to_json(client)
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["name"] == "test-client"

        # Test deserialize from dict
        deserialized = ModelSerializer.deserialize_from_dict(ClientCreate, data)
        assert deserialized.name == client.name
        assert deserialized.nice_name == client.nice_name

        # Test deserialize from JSON
        deserialized_json = ModelSerializer.deserialize_from_json(ClientCreate, json_str)
        assert deserialized_json.name == client.name

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_model_serializer_complex() -> dict[str, Any]:
    """Test ModelSerializer with complex nested models."""
    test_name = "ModelSerializer - Complex Models"
    try:
        # Test with nested model
        point = PointCreate(
            name="test/point/1",
            client_id=1,
            site_id=1,
            kv_tags={"unit": "degF", "type": "temperature"},
            marker_tags=["sensor", "hvac", "temp"],
            bacnet_data=BACnetData(
                device_id=12345,
                device_address="192.168.1.100",
                object_type="analogInput",
                object_index=1,
                object_name="Room Temperature",
            ),
            point_type="bacnet",
            collect_enabled=True,
            collect_interval=300,
        )

        # Serialize and deserialize
        data = ModelSerializer.serialize_to_dict(point)
        assert data["name"] == "test/point/1"
        assert data["kv_tags"]["unit"] == "degF"
        assert "sensor" in data["marker_tags"]
        assert data["bacnet_data"]["device_id"] == 12345

        # Test round trip
        deserialized = ModelSerializer.deserialize_from_dict(PointCreate, data)
        assert deserialized.name == point.name
        assert deserialized.bacnet_data.device_id == 12345

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_bulk_serializer() -> dict[str, Any]:
    """Test BulkSerializer functionality."""
    test_name = "BulkSerializer - List Operations"
    try:
        # Create list of models
        sites = [
            SiteCreate(
                name=f"site-{i}",
                client_id=1,
                nice_name=f"Site {i}",
                address=f"{i} Main St",
                latitude=40.0 + i * 0.1,
                longitude=-74.0 + i * 0.1,
            )
            for i in range(3)
        ]

        # Test serialize list
        data_list = BulkSerializer.serialize_list(sites)
        assert len(data_list) == 3
        assert data_list[0]["name"] == "site-0"
        assert data_list[2]["latitude"] == 40.2

        # Test deserialize list
        deserialized = BulkSerializer.deserialize_list(SiteCreate, data_list)
        assert len(deserialized) == 3
        assert deserialized[1].name == "site-1"

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_hash_serializer() -> dict[str, Any]:
    """Test HashSerializer functionality."""
    test_name = "HashSerializer - Hash Encoding/Decoding"
    try:
        # Test hex to base64 conversion
        hex_hash = "48656c6c6f20576f726c64"  # "Hello World" in hex
        b64_hash = HashSerializer.encode_hash_base64(hex_hash)
        assert b64_hash == base64.b64encode(bytes.fromhex(hex_hash)).decode()

        # Test base64 to hex conversion
        decoded_hex = HashSerializer.decode_hash_base64(b64_hash)
        assert decoded_hex == hex_hash

        # Test normalize hash
        normalized_hex = HashSerializer.normalize_hash(b64_hash, "hex")
        assert normalized_hex == hex_hash

        normalized_b64 = HashSerializer.normalize_hash(hex_hash, "base64")
        assert normalized_b64 == b64_hash

        # Test with real hash
        sha256_hex = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        sha256_b64 = HashSerializer.encode_hash_base64(sha256_hex)
        assert HashSerializer.decode_hash_base64(sha256_b64) == sha256_hex

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_datetime_serializer() -> dict[str, Any]:
    """Test DateTimeSerializer functionality."""
    test_name = "DateTimeSerializer - DateTime Operations"
    try:
        # Test serialize datetime
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        iso_str = DateTimeSerializer.serialize_datetime(dt)
        assert iso_str == "2024-01-15T10:30:45+00:00"

        # Test non-ISO format
        std_str = DateTimeSerializer.serialize_datetime(dt, iso_format=False)
        assert std_str == "2024-01-15 10:30:45"

        # Test deserialize datetime
        deserialized = DateTimeSerializer.deserialize_datetime(iso_str)
        assert deserialized.year == 2024
        assert deserialized.month == 1
        assert deserialized.day == 15

        # Test ensure timezone.utc
        naive_dt = datetime(2024, 1, 15, 10, 30, 45)
        utc_dt = DateTimeSerializer.ensure_utc(naive_dt)
        assert utc_dt.tzinfo == timezone.utc

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_validation_serializer() -> dict[str, Any]:
    """Test ValidationSerializer functionality."""
    test_name = "ValidationSerializer - Validation and Error Handling"
    try:
        # Test valid model
        gateway = GatewayCreate(
            name="test-gateway",
            site="test-site",
            client="test-client",
            primary_mac="00:11:22:33:44:55",
            vpn_ip="10.0.0.1",
        )

        data = ValidationSerializer.validate_and_serialize(gateway)
        assert data["name"] == "test-gateway"

        # Test safe deserialize with valid data
        result = ValidationSerializer.safe_deserialize(GatewayCreate, data)
        assert isinstance(result, GatewayCreate)
        assert result.name == "test-gateway"

        # Test safe deserialize with invalid data
        invalid_data = {"name": 123, "site": None}  # Wrong types
        result = ValidationSerializer.safe_deserialize(GatewayCreate, invalid_data)
        # Should return ErrorResponse on failure
        assert hasattr(result, "error") or hasattr(result, "message")

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_api_response_serializer() -> dict[str, Any]:
    """Test APIResponseSerializer functionality."""
    test_name = "APIResponseSerializer - API Response Formatting"
    try:
        # Test paginated response
        items = [
            UserCreate(
                email=f"user{i}@example.com",
                first_name=f"User{i}",
                last_name="Test",
                password="SecurePassword123!",
                role="user",
            )
            for i in range(3)
        ]

        paginated = APIResponseSerializer.serialize_paginated_response(
            items=items, page=1, per_page=10, total=3
        )

        assert paginated["page"] == 1
        assert paginated["pages"] == 1
        assert paginated["per_page"] == 10
        assert paginated["total"] == 3
        assert len(paginated["items"]) == 3
        assert paginated["items"][0]["email"] == "user0@example.com"

        # Test error response
        error_resp = APIResponseSerializer.serialize_error_response(
            error="Not found",
            details={"resource": "client", "id": 123},
            code="NOT_FOUND",
        )

        assert error_resp["error"] == "Not found"
        assert error_resp["code"] == "NOT_FOUND"
        assert error_resp["details"]["resource"] == "client"
        assert "timestamp" in error_resp

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_auto_detect_model_type() -> dict[str, Any]:
    """Test auto_detect_model_type functionality."""
    test_name = "Auto Detect Model Type"
    try:
        # Test Point detection
        point_data = {
            "client_id": 1,
            "site_id": 2,
            "name": "test/point",
            "bacnet_data": {},
            "marker_tags": [],
        }
        assert auto_detect_model_type(point_data) == "Point"

        # Test Site detection
        site_data = {
            "nice_name": "Test Site",
            "address": "123 Main St",
            "vtron_ip": "192.168.1.1",
        }
        assert auto_detect_model_type(site_data) == "Site"

        # Test Client detection
        client_data = {"nice_name": "Test Client", "address": "456 Oak St"}
        assert auto_detect_model_type(client_data) == "Client"

        # Test DerEvent detection
        event_data = {
            "event_start": "2024-01-01T00:00:00Z",
            "event_end": "2024-01-01T01:00:00Z",
        }
        assert auto_detect_model_type(event_data) == "DerEvent"

        # Test User detection
        user_data = {"email": "test@example.com", "first_name": "Test"}
        assert auto_detect_model_type(user_data) == "User"

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_serialize_for_api() -> dict[str, Any]:
    """Test serialize_for_api functionality."""
    test_name = "Serialize for API"
    try:
        # Create a model with readonly fields
        der_event = DerEventCreate(
            timezone="timezone.utc",
            event_start=datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            event_end=datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
            event_type="curtailment",
            group_name="group-1",
            title="Test Event",
            description="Test curtailment event",
        )

        # Serialize for API (should exclude readonly fields)
        data = serialize_for_api(der_event, exclude_readonly=True)
        assert "timezone" in data
        assert "event_start" in data
        assert "id" not in data  # Should be excluded
        assert "created" not in data  # Should be excluded
        assert "updated" not in data  # Should be excluded

        # Serialize without excluding readonly
        data_with_readonly = serialize_for_api(der_event, exclude_readonly=False)
        # For Create models, these fields might not exist anyway
        assert "timezone" in data_with_readonly

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_deserialize_from_api() -> dict[str, Any]:
    """Test deserialize_from_api functionality."""
    test_name = "Deserialize from API"
    try:
        # Test strict deserialization
        data = {
            "identity": "test-agent",
            "package_name": "test-package",
            "revision": "1.0.0",
            "tag": "latest",
            "active": True,
        }

        agent = deserialize_from_api(VolttronAgentCreate, data, strict=True)
        assert agent.identity == "test-agent"
        assert agent.package_name == "test-package"

        # Test non-strict deserialization (ignores unknown fields)
        data_with_extra = {
            **data,
            "unknown_field": "should be ignored",
            "another_unknown": 123,
        }

        agent_non_strict = deserialize_from_api(VolttronAgentCreate, data_with_extra, strict=False)
        assert agent_non_strict.identity == "test-agent"

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_timeseries_serialization() -> dict[str, Any]:
    """Test serialization of timeseries data."""
    test_name = "Timeseries Data Serialization"
    try:
        # Create timeseries samples
        samples = [
            PointSample(
                name="site1/temp",
                value="72.5",
                time=datetime(2024, 1, 1, i, 0, 0, tzinfo=timezone.utc),
            )
            for i in range(3)
        ]

        # Create timeseries data
        ts_data = TimeseriesData(point_samples=samples)

        # Serialize
        data = ModelSerializer.serialize_to_dict(ts_data)
        assert "point_samples" in data
        assert len(data["point_samples"]) == 3
        assert data["point_samples"][0]["name"] == "site1/temp"
        assert data["point_samples"][0]["value"] == "72.5"

        # Deserialize
        deserialized = ModelSerializer.deserialize_from_dict(TimeseriesData, data)
        assert len(deserialized.point_samples) == 3
        assert deserialized.point_samples[1].time.hour == 1

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_weather_data_serialization() -> dict[str, Any]:
    """Test serialization of weather data."""
    test_name = "Weather Data Serialization"
    try:
        # Create weather data
        weather = WeatherData(
            temp=PointSample(
                name="weather/temp",
                value="68.5",
                time=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            ),
            humidity=PointSample(
                name="weather/humidity",
                value="45",
                time=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            ),
            pressure=PointSample(
                name="weather/pressure",
                value="1013.25",
                time=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            ),
        )

        # Serialize
        data = ModelSerializer.serialize_to_dict(weather)
        assert data["temp"]["value"] == "68.5"
        assert data["humidity"]["value"] == "45"
        assert data["pressure"]["value"] == "1013.25"

        # JSON round trip
        json_str = ModelSerializer.serialize_to_json(weather)
        deserialized = ModelSerializer.deserialize_from_json(WeatherData, json_str)
        assert deserialized.temp.value == "68.5"

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_hawke_config_serialization() -> dict[str, Any]:
    """Test serialization of Hawke configurations."""
    test_name = "Hawke Config Serialization"
    try:
        # Create Hawke config
        config = HawkeConfigCreate(
            content_blob='{"config": "data", "version": "1.0"}',
            content_hash="abcdef123456",
        )

        # Serialize
        data = ModelSerializer.serialize_to_dict(config)
        assert data["content_blob"] == '{"config": "data", "version": "1.0"}'
        assert data["content_hash"] == "abcdef123456"

        # Test with base64 hash
        b64_hash = HashSerializer.encode_hash_base64("abcdef123456")
        config_b64 = HawkeConfigCreate(
            content_blob='{"config": "data"}',
            content_hash=b64_hash,
        )

        data_b64 = ModelSerializer.serialize_to_dict(config_b64)
        assert data_b64["content_hash"] == b64_hash

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_agent_config_serialization() -> dict[str, Any]:
    """Test serialization of agent configurations."""
    test_name = "Agent Config Serialization"
    try:
        # Create agent config
        config = AgentConfigCreate(
            agent_identity="platform.agent",
            config_name="config",
            config_hash="fedcba654321",
            blob='{"setting1": "value1", "setting2": 42}',
            active=True,
        )

        # Serialize
        data = ModelSerializer.serialize_to_dict(config)
        assert data["agent_identity"] == "platform.agent"
        assert data["config_name"] == "config"
        assert data["active"] is True

        # Deserialize
        deserialized = ModelSerializer.deserialize_from_dict(AgentConfigCreate, data)
        assert deserialized.blob == '{"setting1": "value1", "setting2": 42}'

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def test_error_handling() -> dict[str, Any]:
    """Test error handling in serializers."""
    test_name = "Error Handling"
    try:
        # Test invalid JSON deserialization
        try:
            ModelSerializer.deserialize_from_json(ClientCreate, "invalid json {")
        except DeserializationError as e:
            assert "Invalid JSON format" in str(e)

        # Test invalid data type
        try:
            ModelSerializer.deserialize_from_dict(SiteCreate, {"name": 123, "client": None})
        except DeserializationError as e:
            assert "Validation failed" in str(e)

        # Test invalid hex hash
        try:
            HashSerializer.encode_hash_base64("invalid-hex")
        except SerializationError as e:
            assert "Invalid hex hash format" in str(e)

        # Test invalid base64 hash
        try:
            HashSerializer.decode_hash_base64("invalid-base64!")
        except DeserializationError as e:
            assert "Invalid base64 hash format" in str(e)

        return {"test_name": test_name, "passed": True, "error": None}
    except Exception as e:
        return {"test_name": test_name, "passed": False, "error": str(e)}


def run_all_serializer_tests() -> list[dict[str, Any]]:
    """Run all serializer tests and return results."""
    tests = [
        test_model_serializer_basic,
        test_model_serializer_complex,
        test_bulk_serializer,
        test_hash_serializer,
        test_datetime_serializer,
        test_validation_serializer,
        test_api_response_serializer,
        test_auto_detect_model_type,
        test_serialize_for_api,
        test_deserialize_from_api,
        test_timeseries_serialization,
        test_weather_data_serialization,
        test_hawke_config_serialization,
        test_agent_config_serialization,
        test_error_handling,
    ]

    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)

    return results


if __name__ == "__main__":
    # Run tests if executed directly
    results = run_all_serializer_tests()

    print("=" * 60)
    print("SERIALIZER TEST RESULTS")
    print("=" * 60)

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status} | {result['test_name']}")
        if not result["passed"]:
            print(f"     Error: {result['error']}")

    print("=" * 60)
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"Total: {total} | Passed: {passed} | Failed: {total - passed}")
