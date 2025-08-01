"""Tests for utility functions."""

from unittest.mock import Mock, call

import pytest

from aceiot_models_cli.utils import (
    PaginatedResults,
    batch_process,
    convert_api_response_to_points,
    convert_samples_to_models,
    get_api_results_paginated,
    post_to_api,
    process_points_from_api,
)


class TestPaginatedResults:
    """Test cases for PaginatedResults iterator."""

    def test_single_page_iteration(self):
        """Test iteration with single page of results."""
        mock_func = Mock(return_value={"items": [1, 2, 3], "page": 1, "pages": 1})

        paginator = PaginatedResults(mock_func, per_page=10)
        results = list(paginator)

        assert len(results) == 1
        assert results[0] == [1, 2, 3]
        mock_func.assert_called_once_with(page=1, per_page=10)

    def test_multi_page_iteration(self):
        """Test iteration with multiple pages."""
        responses = [
            {"items": [1, 2, 3], "page": 1, "total_pages": 3},
            {"items": [4, 5, 6], "page": 2, "total_pages": 3},
            {"items": [7, 8], "page": 3, "total_pages": 3},
        ]
        mock_func = Mock(side_effect=responses)

        paginator = PaginatedResults(mock_func, per_page=3)
        results = list(paginator)

        assert len(results) == 3
        assert results[0] == [1, 2, 3]
        assert results[1] == [4, 5, 6]
        assert results[2] == [7, 8]
        assert mock_func.call_count == 3

    def test_all_items(self):
        """Test getting all items from all pages."""
        responses = [
            {"items": [1, 2, 3], "page": 1, "total_pages": 2},
            {"items": [4, 5, 6], "page": 2, "total_pages": 2},
        ]
        mock_func = Mock(side_effect=responses)

        paginator = PaginatedResults(mock_func, per_page=3)
        all_items = paginator.all_items()

        assert all_items == [1, 2, 3, 4, 5, 6]


class TestBatchProcess:
    """Test cases for batch_process function."""

    def test_batch_processing(self):
        """Test processing items in batches."""
        items = list(range(10))
        mock_process = Mock(return_value="processed")

        results = batch_process(items, mock_process, batch_size=3)

        assert len(results) == 4  # 10 items / 3 per batch = 4 batches
        assert mock_process.call_count == 4

        # Check batch contents
        calls = mock_process.call_args_list
        assert calls[0] == call([0, 1, 2])
        assert calls[1] == call([3, 4, 5])
        assert calls[2] == call([6, 7, 8])
        assert calls[3] == call([9])

    def test_batch_processing_with_progress(self):
        """Test batch processing with progress callback."""
        items = list(range(5))
        mock_process = Mock(return_value="processed")
        mock_progress = Mock()

        batch_process(items, mock_process, batch_size=2, progress_callback=mock_progress)

        # Check progress callbacks
        progress_calls = mock_progress.call_args_list
        assert progress_calls[0] == call(2, 5)
        assert progress_calls[1] == call(4, 5)
        assert progress_calls[2] == call(5, 5)  # Final progress

    def test_batch_processing_error_handling(self):
        """Test error handling in batch processing."""
        items = list(range(5))
        mock_process = Mock(side_effect=["success", Exception("Batch failed"), "success"])

        with pytest.raises(Exception, match="Batch failed"):
            batch_process(items, mock_process, batch_size=2)

        # Should have attempted first two batches
        assert mock_process.call_count == 2


class TestApiHelpers:
    """Test cases for API helper functions."""

    def test_get_api_results_paginated(self):
        """Test paginated API results retrieval."""
        # Mock API function
        mock_api_func = Mock(
            side_effect=[
                {"items": [1, 2], "page": 1, "total_pages": 2},
                {"items": [3, 4], "page": 2, "total_pages": 2},
            ]
        )

        results = get_api_results_paginated(mock_api_func, per_page=2)

        assert results == [1, 2, 3, 4]  # Returns flattened list of all items

        # Check API calls
        calls = mock_api_func.call_args_list
        assert calls[0] == call(page=1, per_page=2)
        assert calls[1] == call(page=2, per_page=2)

    def test_post_to_api(self):
        """Test POST helper function."""
        mock_client = Mock()
        mock_client._request.return_value = {"success": True}

        data = {"key": "value"}
        params = {"param": "test"}

        result = post_to_api(mock_client, "/test/endpoint", data, params)

        assert result == {"success": True}
        mock_client._request.assert_called_once_with(
            "POST", "/test/endpoint", data=data, params=params
        )

    def test_process_points_from_api(self):
        """Test processing points from API."""
        from aceiot_models import Point

        api_data = [
            {
                "id": 123,
                "name": "test/point",
                "point_type": "bacnet",
                "marker_tags": [],
                "kv_tags": {},
                "collect_config": {},
                "collect_enabled": True,
                "collect_interval": 300,
                "created": "2024-01-01T10:00:00Z",
                "updated": "2024-01-01T12:00:00Z",
                "site_id": 1,
                "client_id": 1,
                "bacnet_data": {
                    "device_id": 123,
                    "device_address": "192.168.1.100",
                    "device_name": "Controller",
                    "device_description": "Test Controller",
                    "object_type": "analog-input",
                    "object_index": 1,
                    "object_name": "Temperature",
                    "present_value": "72.5",
                },
            }
        ]

        points = list(process_points_from_api(api_data))

        assert len(points) == 1
        # Should return Point model objects
        assert isinstance(points[0], Point)
        assert points[0].name == "test/point"
        assert points[0].bacnet_data is not None
        assert points[0].bacnet_data.device_id == 123

    def test_convert_samples_to_models(self):
        """Test converting sample data to Sample models."""
        from aceiot_models import Sample

        sample_data = [
            {
                "name": "test/point1",
                "time": "2024-01-01T10:00:00Z",
                "value": 25.5,
            },
            {
                "name": "test/point2",
                "time": "2024-01-01T10:01:00Z",
                "value": 26.0,
            },
        ]

        samples = convert_samples_to_models(sample_data)

        assert len(samples) == 2
        for sample in samples:
            assert isinstance(sample, Sample)
            assert hasattr(sample, "name")
            assert hasattr(sample, "time")
            assert hasattr(sample, "value")

    def test_convert_api_response_to_points(self):
        """Test converting API response to use Point models."""
        from aceiot_models import Point

        api_response = {
            "items": [
                {
                    "id": 123,
                    "name": "test/point",
                    "point_type": "bacnet",
                    "site_id": 1,
                    "client_id": 1,
                    "created": "2024-01-01T10:00:00Z",
                    "updated": "2024-01-01T12:00:00Z",
                    "bacnet_data": {
                        "device_id": 123,
                        "object_type": "analog-input",
                        "object_index": 1,
                    },
                }
            ],
            "page": 1,
            "pages": 1,
        }

        result = convert_api_response_to_points(api_response)

        assert len(result) == 1
        point = result[0]
        assert isinstance(point, Point)
        assert point.name == "test/point"
