"""Tests for site commands."""

import json

from aceiot_models_cli.cli import cli


class TestSiteCommands:
    """Test site-related commands."""

    def test_list_sites_table(self, runner, mock_load_config, mock_api_client_class):
        """Test listing sites in table format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_sites.return_value = {
            "items": [
                {
                    "id": 1,
                    "name": "site1",
                    "client": "client1",
                    "nice_name": "Site One",
                    "address": "123 Site St",
                    "archived": False,
                },
                {
                    "id": 2,
                    "name": "site2",
                    "client": "client2",
                    "nice_name": "Site Two",
                    "address": "456 Site Ave",
                    "archived": True,
                },
            ],
            "page": 1,
            "pages": 1,
            "per_page": 10,
            "total": 2,
        }

        result = runner.invoke(cli, ["sites", "list"])
        assert result.exit_code == 0
        assert "Site One" in result.output
        assert "Site Two" in result.output
        assert "123 Site St" in result.output
        mock_api_client.get_sites.assert_called_once_with(
            page=1,
            per_page=10,
            collect_enabled=False,
            show_archived=False,
        )

    def test_list_sites_with_filters(self, runner, mock_load_config, mock_api_client_class):
        """Test listing sites with filters."""
        mock_api_client = mock_api_client_class.return_value
        # Mock get_client_sites for when client_name is provided
        mock_api_client.get_client_sites.return_value = {"items": [], "total": 0}

        result = runner.invoke(
            cli,
            [
                "sites",
                "list",
                "--client-name",
                "client1",
                "--collect-enabled",
                "--show-archived",
                "--page",
                "2",
                "--per-page",
                "20",
            ],
        )
        assert result.exit_code == 0
        # When client_name is provided, get_client_sites is called instead
        mock_api_client.get_client_sites.assert_called_once_with(
            client_name="client1",
            page=2,
            per_page=20,
        )

    def test_list_sites_json(self, runner, mock_load_config, mock_api_client_class):
        """Test listing sites in JSON format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_sites.return_value = {
            "items": [{"id": 1, "name": "site1", "client": "client1"}],
            "total": 1,
        }

        result = runner.invoke(cli, ["--output", "json", "sites", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "site1"

    def test_get_site_table(self, runner, mock_load_config, mock_api_client_class):
        """Test getting a specific site in table format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_site.return_value = {
            "id": 1,
            "name": "test-site",
            "nice_name": "Test Site",
            "client": "test-client",
            "address": "789 Test Blvd",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York",
            "archived": False,
        }

        result = runner.invoke(cli, ["sites", "get", "test-site"])
        assert result.exit_code == 0
        assert "Site: test-site" in result.output
        assert "Nice Name: Test Site" in result.output
        assert "Client: test-client" in result.output
        assert "Address: 789 Test Blvd" in result.output
        assert "Timezone: America/New_York" in result.output
        mock_api_client.get_site.assert_called_once_with("test-site")

    def test_get_site_json(self, runner, mock_load_config, mock_api_client_class):
        """Test getting a specific site in JSON format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_site.return_value = {
            "id": 1,
            "name": "test-site",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }

        result = runner.invoke(cli, ["--output", "json", "sites", "get", "test-site"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "test-site"
        assert data["latitude"] == 40.7128
        assert data["longitude"] == -74.0060

    def test_get_site_error(self, runner, mock_load_config, mock_api_client_class):
        """Test getting a site that doesn't exist."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_site.side_effect = Exception("Site not found")

        result = runner.invoke(cli, ["sites", "get", "nonexistent"])
        assert result.exit_code == 1
        assert "Failed to get site" in result.output

    def test_list_sites_error(self, runner, mock_load_config, mock_api_client_class):
        """Test listing sites with API error."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_sites.side_effect = Exception("API error")

        result = runner.invoke(cli, ["sites", "list"])
        assert result.exit_code == 1
        assert "Failed to list sites" in result.output
