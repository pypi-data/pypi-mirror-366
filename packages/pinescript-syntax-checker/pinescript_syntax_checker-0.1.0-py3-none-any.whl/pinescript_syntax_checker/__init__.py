"""
PineScript Syntax Checker MCP Server

A Model Context Protocol (MCP) server for checking PineScript syntax using TradingView's API.
"""

__version__ = "0.1.0"
__author__ = "erevus"

from .server import app, check_syntax

__all__ = ["app", "check_syntax"] 