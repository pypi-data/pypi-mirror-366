# Cursor MCP Manager
[![PyPI version](https://img.shields.io/pypi/v/cursor-mcp)](https://pypi.org/project/cursor-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/cursor-mcp.svg)](https://pypi.org/project/cursor-mcp/)

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=cursor-manager&config=JTdCJTIyY29tbWFuZCUyMiUzQSUyMnV2eCUyMGN1cnNvci1tY3AlMjIlN0Q%3D)

An MCP (Model Context Protocol) server that allows you to manage Cursor IDE's MCP configuration through tools.

## Features

- **List MCP Servers**: View all configured MCP servers
- **Add MCP Server**: Add new MCP servers to your configuration (STDIO or HTTP)
- **Remove MCP Server**: Remove existing MCP servers
- **Update MCP Server**: Modify server configurations
- **Refresh Server**: Restart a specific MCP server with automatic process cleanup
- **Kill Server**: Manually stop a running MCP server
- **Process Monitoring**: Check server status and running processes
- **Log Collection**: View logs from running MCP servers
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Docker Support**: Special handling for Docker-based MCP servers

**Note**: Cursor automatically detects changes to the `mcp.json` file and reloads servers without requiring a restart.

## Installation

### Quick Install with uvx (Recommended)

The simplest way to use cursor-mcp is with `uvx` (no installation required!):

```json
{
  "mcpServers": {
    "cursor-manager": {
      "command": "uvx",
      "args": ["cursor-mcp"]
    }
  }
}
```

That's it! This will automatically download and run the latest version from PyPI.

### Install from PyPI

```bash
# Install globally as a tool
uv tool install cursor-mcp

# Or use pip
pip install cursor-mcp
```

### From source

```bash
git clone https://github.com/hud-evals/hud-cursor-manager
cd hud-cursor-manager
uv sync
uv run cursor-mcp
```

## How it Works

1. **First Connection**: When Cursor starts the STDIO proxy, it automatically spawns a persistent HTTP server in the background
2. **Subsequent Connections**: New Cursor windows connect to the existing HTTP server
3. **Shared State**: All windows share the same server state, logs, and configuration
4. **Persistence**: The HTTP server continues running even after all Cursor windows are closed

### Stopping the Background Server

The HTTP server runs on port 48765 by default. To stop it:

```bash
# Using the manager CLI
uvx --from cursor-mcp cursor-manager stop

# Or find and kill the process manually
# Windows:
netstat -ano | findstr :48765
taskkill /F /PID <PID>

# macOS/Linux:
lsof -i :48765
kill -9 <PID>
```

You can also set a custom port using the `CURSOR_MCP_PORT` environment variable.

## Usage

Once configured, the following tools are available in Cursor:

- **list_mcp_servers** - View all configured MCP servers
- **add_mcp_server** - Add a new MCP server configuration
- **remove_mcp_server** - Remove an MCP server
- **update_mcp_server** - Modify server settings
- **refresh_mcp_server** - Restart a server
- **kill_mcp_server** - Stop a running server
- **check_server_status** - Check if a server is running
- **list_running_servers** - List all running MCP processes
- **get_server_logs** - View server logs (last 100 lines)

## Development

```bash
# Install dependencies
uv sync

# Run the server
uv run cursor-mcp

# Run tests
uv run pytest tests/
```

## Known Limitations

### Tool List Updates in Active Conversations

When you refresh an MCP server that has new or updated tools, the changes will be available on your next message in the conversation. Cursor refreshes the tool list when you send a new message.

**Note**: Simply send another message after refreshing to see the updated tools - no need to start a new conversation.

## License

MIT License - see LICENSE file for details.