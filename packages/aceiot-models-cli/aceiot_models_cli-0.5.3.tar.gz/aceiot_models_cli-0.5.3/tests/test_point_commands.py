"""Tests for point commands."""

import json

from aceiot_models_cli.cli import cli


class TestPointCommands:
    """Test point-related commands."""

    def test_list_points_table(self, runner, mock_load_config, mock_api_client_class):
        """Test listing points in table format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_points.return_value = {
            "items": [
                {
                    "id": 1,
                    "name": "site1/temp/sensor1",
                    "site": "site1",
                    "point_type": "bacnet",
                    "collect_enabled": True,
                    "collect_interval": 300,
                    "updated": "2024-01-15T10:30:00Z",
                },
                {
                    "id": 2,
                    "name": "site1/hum/sensor1",
                    "site": "site1",
                    "point_type": "bacnet",
                    "collect_enabled": False,
                    "collect_interval": 600,
                    "updated": "2024-01-15T11:00:00Z",
                },
            ],
            "page": 1,
            "pages": 1,
            "per_page": 10,
            "total": 2,
        }

        result = runner.invoke(cli, ["points", "list"])
        assert result.exit_code == 0
        assert "site1/temp/sensor1" in result.output
        assert "site1/hum/sensor1" in result.output
        assert "bacnet" in result.output
        assert "Yes" in result.output  # collect_enabled
        assert "300" in result.output  # collect_interval
        mock_api_client.get_points.assert_called_once_with(page=1, per_page=10)

    def test_list_points_for_site(self, runner, mock_load_config, mock_api_client_class):
        """Test listing points for a specific site."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_site_points.return_value = {
            "items": [{"id": 1, "name": "site1/temp/sensor1"}],
            "total": 1,
        }

        result = runner.invoke(cli, ["points", "list", "--site", "site1"])
        assert result.exit_code == 0
        mock_api_client.get_site_points.assert_called_once_with("site1", page=1, per_page=10)

    def test_list_points_json(self, runner, mock_load_config, mock_api_client_class):
        """Test listing points in JSON format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_points.return_value = {
            "items": [{"id": 1, "name": "site1/temp/sensor1", "point_type": "bacnet"}],
            "total": 1,
        }

        result = runner.invoke(cli, ["--output", "json", "points", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "site1/temp/sensor1"

    def test_get_timeseries_table(self, runner, mock_load_config, mock_api_client_class):
        """Test getting timeseries data in table format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_point_timeseries.return_value = {
            "point_samples": [
                {
                    "name": "site1/temp/sensor1",
                    "value": "72.5",
                    "time": "2024-01-01T00:00:00Z",
                },
                {
                    "name": "site1/temp/sensor1",
                    "value": "73.0",
                    "time": "2024-01-01T00:05:00Z",
                },
                {
                    "name": "site1/temp/sensor1",
                    "value": "72.8",
                    "time": "2024-01-01T00:10:00Z",
                },
            ]
        }

        result = runner.invoke(
            cli,
            [
                "points",
                "timeseries",
                "site1/temp/sensor1",
                "--start",
                "2024-01-01T00:00:00Z",
                "--end",
                "2024-01-01T01:00:00Z",
            ],
        )
        assert result.exit_code == 0
        assert "72.5" in result.output
        assert "73.0" in result.output
        assert "72.8" in result.output
        assert "2024-01-01T00:00:00Z" in result.output
        assert "Total samples: 3" in result.output
        mock_api_client.get_point_timeseries.assert_called_once_with(
            "site1/temp/sensor1",
            "2024-01-01T00:00:00Z",
            "2024-01-01T01:00:00Z",
        )

    def test_get_timeseries_json(self, runner, mock_load_config, mock_api_client_class):
        """Test getting timeseries data in JSON format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_point_timeseries.return_value = {
            "point_samples": [
                {
                    "name": "site1/temp/sensor1",
                    "value": "72.5",
                    "time": "2024-01-01T00:00:00Z",
                }
            ]
        }

        result = runner.invoke(
            cli,
            [
                "--output",
                "json",
                "points",
                "timeseries",
                "site1/temp/sensor1",
                "--start",
                "2024-01-01T00:00:00Z",
                "--end",
                "2024-01-01T01:00:00Z",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["point_samples"]) == 1
        assert data["point_samples"][0]["value"] == "72.5"

    def test_get_timeseries_no_data(self, runner, mock_load_config, mock_api_client_class):
        """Test getting timeseries data with no results."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_point_timeseries.return_value = {"point_samples": []}

        result = runner.invoke(
            cli,
            [
                "points",
                "timeseries",
                "site1/temp/sensor1",
                "--start",
                "2024-01-01T00:00:00Z",
                "--end",
                "2024-01-01T01:00:00Z",
            ],
        )
        assert result.exit_code == 0
        assert "No data found" in result.output

    def test_get_timeseries_error(self, runner, mock_load_config, mock_api_client_class):
        """Test getting timeseries data with error."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_point_timeseries.side_effect = Exception("Point not found")

        result = runner.invoke(
            cli,
            [
                "points",
                "timeseries",
                "nonexistent",
                "--start",
                "2024-01-01T00:00:00Z",
                "--end",
                "2024-01-01T01:00:00Z",
            ],
        )
        assert result.exit_code == 1
        assert "Failed to get timeseries data" in result.output

    def test_list_points_error(self, runner, mock_load_config, mock_api_client_class):
        """Test listing points with API error."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_points.side_effect = Exception("API error")

        result = runner.invoke(cli, ["points", "list"])
        assert result.exit_code == 1
        assert "Failed to list points" in result.output
