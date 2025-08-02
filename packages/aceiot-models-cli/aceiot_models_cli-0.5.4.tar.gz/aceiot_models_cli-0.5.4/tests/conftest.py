"""Pytest configuration and fixtures."""

from unittest.mock import Mock, patch

import pytest
from aceiot_models.api import APIClient
from click.testing import CliRunner

from aceiot_models_cli.config import Config


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return Config(
        api_url="https://test.api.com",
        api_key="test-api-key",
        output_format="table",
        timeout=30,
    )


@pytest.fixture
def mock_api_client():
    """Create a mock API client."""
    client = Mock(spec=APIClient)
    return client


@pytest.fixture
def mock_load_config(mock_config):
    """Mock the load_config function."""
    with patch("aceiot_models_cli.cli.load_config") as mock:
        mock.return_value = mock_config
        yield mock


@pytest.fixture
def mock_api_client_class(mock_api_client):
    """Mock the APIClient class."""
    with patch("aceiot_models_cli.cli.APIClient") as mock:
        mock.return_value = mock_api_client
        yield mock
