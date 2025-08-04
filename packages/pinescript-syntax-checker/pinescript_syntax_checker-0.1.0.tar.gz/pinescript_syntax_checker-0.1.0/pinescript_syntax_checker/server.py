#!/usr/bin/env python3
"""
MCP Server for PineScript syntax checking
"""

import asyncio
from typing import Any, Optional, Dict, Union
import httpx
from mcp.server.fastmcp import FastMCP
from .pinescript_checker import PineScriptChecker

app = FastMCP('pinescript-syntax-checker')

@app.tool()
async def check_syntax(pine_code: str) -> Optional[Dict[str, Any]]:
    """
    Check PineScript syntax using TradingView's API

    Args:
        pine_code: PineScript code to check

    Returns:
        result: Dictionary containing syntax check results
    """
    checker = PineScriptChecker()

    try:
        result = await checker.check_syntax(pine_code)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': f'Check failed: {str(e)}',
            'errors': []
        }

def main():
    """Entry point for the MCP server."""
    app.run()

if __name__ == "__main__":
    main() 