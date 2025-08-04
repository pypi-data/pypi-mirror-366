# PineScript Syntax Checker MCP Server

A Model Context Protocol (MCP) server for checking PineScript syntax using TradingView's API.

## Features

- Check PineScript syntax using TradingView's official API
- MCP-compatible server with httpx for async HTTP requests
- Detailed error reporting with line and column information

## Quick Start

### Option 1: Using uvx (Recommended)

```bash
# Install and run directly
uvx pinescript-syntax-checker

# Or install first, then run
uvx install pinescript-syntax-checker
uvx run pinescript-syntax-checker
```

### Option 2: Using uv

```bash
# Clone and run
git clone https://github.com/erevus-cn/pinescript-syntax-checker.git
cd pinescript-syntax-checker
uv sync
uv run python run_server.py
```

### Option 3: Using pip

```bash
# Install from PyPI
pip install pinescript-syntax-checker

# Run directly
pinescript-syntax-checker

# Or as module
python -m pinescript_syntax_checker.server
```

## MCP Integration

### Install MCP Server

```bash
# If using uvx
uvx pinescript-syntax-checker --mcp-install

# If using local development
uv run mcp install run_server.py
```

### Configure in Cursor

#### Method 1: No Configuration Required (Recommended)

After installing with `uvx`, the server will be automatically available in Cursor.

#### Method 2: Manual Configuration

If you need manual configuration:

1. **Open Cursor Settings**:
   - Press `Cmd+,` (macOS) or `Ctrl+,` (Windows/Linux)
   - Go to "Extensions" → "MCP"

2. **Add Server Configuration**:
   ```json
   {
     "mcpServers": {
       "pinescript-syntax-checker": {
         "command": "python",
         "args": ["-m", "pinescript_syntax_checker.server"]
       }
     }
   }
   ```

3. **Restart Cursor** to load the MCP server

## API

### check_syntax

Checks PineScript syntax using TradingView's API.

**Parameters:**
- `pine_code` (str): The PineScript code to check

## Example

**Input:**
```pinescript
//@version=5
strategy("Test")
plot(close)
```

**Output:**
```json
{
  "success": true,
  "result": {
    "variables": [],
    "functions": [],
    "types": [],
    "enums": [],
    "scopes": []
  }
}
```

## License

MIT License
