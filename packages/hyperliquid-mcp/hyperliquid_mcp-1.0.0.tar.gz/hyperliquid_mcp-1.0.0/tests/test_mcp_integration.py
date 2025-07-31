"""Integration tests for MCP server functionality."""

import os
from unittest.mock import patch

from fastmcp import FastMCP

from hyperliquid_mcp.server import main, mcp


class TestMCPServerIntegration:
    """Test MCP server integration and tool registration."""

    def test_mcp_server_creation(self):
        """Test that MCP server is created correctly."""
        assert isinstance(mcp, FastMCP)
        assert mcp.name == "Hyperliquid MCP Server"

    def test_all_tools_registered(self):
        """Test that all expected tools are registered with the MCP server."""
        expected_tools = {
            # Account tools
            "get_positions",
            "update_leverage",
            "withdraw",
            "get_spot_user_state",
            "get_user_fees",
            # Market data tools
            "get_market_data",
            "calculate_min_order_size",
            "get_candle_data",
            "get_user_fills_by_time",
            "get_funding_rates",
            "get_l2_orderbook",
            # Order management tools
            "place_order",
            "cancel_order",
            "get_open_orders",
            "get_order_status",
            "modify_order",
            "bulk_cancel_orders",
            "cancel_all_orders",
            "get_user_fills",
        }

        # Get registered tool names using the correct FastMCP API
        registered_tools = set(mcp._tool_manager._tools.keys())

        # Check that all expected tools are registered
        missing_tools = expected_tools - registered_tools
        extra_tools = registered_tools - expected_tools

        assert not missing_tools, f"Missing tools: {missing_tools}"
        assert not extra_tools, f"Unexpected tools: {extra_tools}"
        assert registered_tools == expected_tools

    @patch.dict(os.environ, {"HYPERLIQUID_PRIVATE_KEY": "test_key"})
    @patch("hyperliquid_mcp.server.mcp.run")
    @patch("hyperliquid_mcp.server.logger")
    def test_main_with_env_vars(self, mock_logger, mock_run):
        """Test main function with required environment variables."""
        main()

        mock_logger.info.assert_called_with("Starting Hyperliquid MCP Server...")
        mock_run.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    @patch("hyperliquid_mcp.server.mcp.run")
    @patch("hyperliquid_mcp.server.logger")
    def test_main_without_env_vars(self, mock_logger, mock_run):
        """Test main function without required environment variables."""
        main()

        mock_logger.warning.assert_any_call(
            "Missing environment variables: ['HYPERLIQUID_PRIVATE_KEY']"
        )
        mock_logger.warning.assert_any_call(
            "Some trading operations may not be available"
        )
        mock_logger.info.assert_called_with("Starting Hyperliquid MCP Server...")
        mock_run.assert_called_once()

    def test_tool_docstrings(self):
        """Test that all tools have proper docstrings."""
        for tool_name, tool in mcp._tool_manager._tools.items():
            func = tool.fn
            assert func.__doc__ is not None, f"Tool {tool_name} missing docstring"
            assert (
                len(func.__doc__.strip()) > 0
            ), f"Tool {tool_name} has empty docstring"

            # Check that docstring contains Returns section (Args may not be present for no-param functions)
            docstring = func.__doc__
            assert "Returns:" in docstring, f"Tool {tool_name} missing Returns section"

            # Check if function takes parameters and ensure Args section exists if it does
            import inspect

            sig = inspect.signature(func)
            if len(sig.parameters) > 0:
                assert (
                    "Args:" in docstring
                ), f"Tool {tool_name} takes parameters but missing Args section"
