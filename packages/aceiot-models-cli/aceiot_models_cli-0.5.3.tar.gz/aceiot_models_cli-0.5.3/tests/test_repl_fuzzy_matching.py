"""Test fuzzy matching functionality in REPL."""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from aceiot_models_cli.repl.context import ContextType, ReplContext
from aceiot_models_cli.repl.executor import ReplCommandExecutor
from aceiot_models_cli.repl.parser import ParsedCommand


class TestReplFuzzyMatching:
    """Test fuzzy matching in REPL use command."""

    @pytest.fixture
    def executor(self):
        """Create executor with mocked dependencies."""
        click_group = Mock()
        click_ctx = Mock()
        click_ctx.obj = {"output": "table"}
        return ReplCommandExecutor(click_group, click_ctx)

    @pytest.fixture
    def context(self):
        """Create a REPL context."""
        return ReplContext()

    def test_fuzzy_match_exact(self, executor):
        """Test exact match gets highest priority."""
        candidates = [
            ("demo-site", "Demo Site (test-client)"),
            ("demo", "Demo Client"),
            ("site-demo", "Site Demo (prod-client)"),
        ]
        
        result = executor._fuzzy_match("demo", candidates)
        
        # Exact match should be first
        assert len(result) == 3
        assert result[0][0] == "demo"
        
    def test_fuzzy_match_prefix(self, executor):
        """Test prefix matching."""
        candidates = [
            ("test-site-1", "Test Site 1"),
            ("production-site", "Production Site"),
            ("test-site-2", "Test Site 2"),
            ("site-test", "Site Test"),
        ]
        
        result = executor._fuzzy_match("test", candidates)
        
        # Prefix matches should come first
        assert len(result) == 3
        assert result[0][0] == "test-site-1"
        assert result[1][0] == "test-site-2"
        assert result[2][0] == "site-test"
        
    def test_fuzzy_match_contains(self, executor):
        """Test contains matching."""
        candidates = [
            ("prod-west-1", "Production West 1"),
            ("dev-west-2", "Development West 2"),
            ("east-prod-1", "East Production 1"),
        ]
        
        result = executor._fuzzy_match("west", candidates)
        
        assert len(result) == 2
        assert "west" in result[0][0]
        assert "west" in result[1][0]
        
    def test_fuzzy_match_description(self, executor):
        """Test matching in description."""
        candidates = [
            ("gw-001", "Test Gateway at Site A"),
            ("gw-002", "Production Gateway"),
            ("gw-003", "Test Gateway at Site B"),
        ]
        
        result = executor._fuzzy_match("test", candidates)
        
        assert len(result) == 2
        # Should match items with "Test" in description
        matched_names = [r[0] for r in result]
        assert "gw-001" in matched_names
        assert "gw-003" in matched_names
        
    def test_fuzzy_match_token(self, executor):
        """Test token-based matching."""
        candidates = [
            ("demo-site-west", "Demo Site West"),
            ("prod-site-east", "Production Site East"),
            ("demo-gateway-west", "Demo Gateway West"),
        ]
        
        result = executor._fuzzy_match("demo west", candidates)
        
        assert len(result) == 2
        # Should match items containing both "demo" and "west"
        matched_names = [r[0] for r in result]
        assert "demo-site-west" in matched_names
        assert "demo-gateway-west" in matched_names
        
    def test_fuzzy_match_case_insensitive(self, executor):
        """Test case-insensitive matching."""
        candidates = [
            ("Demo-Site", "Demo Site"),
            ("PROD-SITE", "Production Site"),
            ("test-site", "Test Site"),
        ]
        
        result = executor._fuzzy_match("DEMO", candidates)
        
        assert len(result) == 1
        assert result[0][0] == "Demo-Site"
        
    def test_fuzzy_match_empty_filter(self, executor):
        """Test empty filter returns all candidates."""
        candidates = [
            ("site1", "Site 1"),
            ("site2", "Site 2"),
        ]
        
        result = executor._fuzzy_match("", candidates)
        
        assert len(result) == 2
        assert result == candidates
        
    @patch('aceiot_models_cli.repl.executor.click')
    def test_use_command_with_filter_single_match(self, mock_click, executor, context):
        """Test use command with filter that returns single match auto-selects."""
        # Mock API client
        mock_client = Mock()
        mock_client.get_sites.return_value = {
            "items": [
                {"name": "demo-site", "client_name": "test-client"},
                {"name": "prod-site", "client_name": "test-client"},
                {"name": "test-site", "client_name": "test-client"},
            ]
        }
        executor.click_ctx.obj["client"] = mock_client
        
        # Mock successful switch
        with patch.object(executor, '_switch_to_context', return_value="Switched to site context: demo-site"):
            # Execute use command with filter
            parsed_cmd = ParsedCommand(
                command_path=["use"],
                arguments=["site", "demo-site"],
                options={},
                context_args={},
                raw_input="use site demo-site"
            )
            result = executor._handle_use_command(["site", "demo-site"], context)
            
            # Should auto-select the only match
            assert "Auto-selecting" in result or "Switched to site context: demo-site" in result
            
    @patch('aceiot_models_cli.repl.executor.click')
    def test_use_command_with_filter_multiple_matches(self, mock_click, executor, context):
        """Test use command with filter that returns multiple matches shows table."""
        # Mock API client
        mock_client = Mock()
        mock_client.get_sites.return_value = {
            "items": [
                {"name": "test-site-1", "client_name": "test-client"},
                {"name": "test-site-2", "client_name": "test-client"},
                {"name": "prod-site", "client_name": "test-client"},
            ]
        }
        executor.click_ctx.obj["client"] = mock_client
        
        # Mock user selection
        mock_click.prompt.return_value = 1
        
        # Mock the console
        mock_console = Mock()
        executor.console = mock_console
        
        # Execute use command with filter
        with patch.object(executor, '_switch_to_context', return_value="Switched to site context: test-site-1"):
            result = executor._handle_use_command(["site", "test"], context)
            
            # Should show filtered table
            mock_console.print.assert_called_once()
            # Table should have been printed with filtered results
            
    def test_use_command_with_filter_no_matches(self, executor, context):
        """Test use command with filter that returns no matches."""
        # Mock API client
        mock_client = Mock()
        mock_client.get_sites.return_value = {
            "items": [
                {"name": "demo-site", "client_name": "test-client"},
                {"name": "prod-site", "client_name": "test-client"},
            ]
        }
        executor.click_ctx.obj["client"] = mock_client
        
        # Execute use command with filter that won't match
        result = executor._handle_use_command(["site", "nonexistent"], context)
        
        # Should return error message
        assert "No sites found matching 'nonexistent'" in result
        assert "Use 'use site' without a filter" in result
