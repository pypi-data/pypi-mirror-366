"""Centralized logging configuration for Hyperliquid MCP."""

import logging
import os
import tempfile
from typing import Optional


def suppress_fastmcp_logging() -> None:
    """Suppress fastmcp internal logging messages."""
    # FastMCP uses a specific logger naming pattern: FastMCP.{module}
    for logger_name in ["FastMCP", "FastMCP.fastmcp.server.server"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.ERROR)
        logger.handlers.clear()
        logger.propagate = False


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    include_console: bool = True,
) -> None:
    """
    Setup centralized logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, uses temp directory
        include_console: Whether to include console output
    """
    if log_file is None:
        log_dir = tempfile.gettempdir()
        log_file = os.path.join(log_dir, "hyperliquid_mcp.log")

    # Configure logging format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Add file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Add console handler if requested
    if include_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    else:
        suppress_fastmcp_logging()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
