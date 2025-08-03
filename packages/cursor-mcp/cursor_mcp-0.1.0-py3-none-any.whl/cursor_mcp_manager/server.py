"""Cursor MCP Manager Server - Manages Cursor IDE MCP configurations."""

import atexit
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel, Field, model_validator

from .active_log_collector import clear_server_logs, get_all_collected_servers, start_log_collection
from .active_log_collector import get_server_logs as get_collected_logs
from .process_monitor import MCPProcessMonitor
from .process_watcher import get_process_watcher, handle_server_refresh

# Initialize FastMCP server
mcp = FastMCP("cursor-mcp-manager")

# Lifecycle logging
LIFECYCLE_LOG_PATH = Path(__file__).parent.parent.parent / "logs" / "cursor-mcp-lifecycle.log"


def log_lifecycle(event: str, details: str = ""):
    """Log lifecycle events to understand how Cursor manages MCP servers."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    pid = os.getpid()
    message = f"[{timestamp}] [PID:{pid}] {event}"
    if details:
        message += f" - {details}"

    try:
        # Ensure logs directory exists
        LIFECYCLE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LIFECYCLE_LOG_PATH, "a") as f:
            f.write(message + "\n")
            f.flush()
    except Exception as e:
        # If we can't write to the log, at least try stderr
        print(f"Lifecycle log error: {e}", file=sys.stderr)


# Log server startup
log_lifecycle("SERVER_STARTING", f"Python {sys.version.split()[0]}, Args: {sys.argv}")


# Register cleanup handler
def cleanup_handler():
    log_lifecycle("SERVER_SHUTTING_DOWN", "Cleanup handler called")


atexit.register(cleanup_handler)

# Configuration constants
if sys.platform == "win32":
    CURSOR_CONFIG_PATH = Path(os.environ["USERPROFILE"]) / ".cursor" / "mcp.json"
else:
    CURSOR_CONFIG_PATH = Path.home() / ".cursor" / "mcp.json"


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""

    # STDIO configuration
    command: str | None = Field(None, description="Command to execute the server")
    args: list[str] = Field(default_factory=list, description="Arguments for the command")
    env: dict[str, str] | None = Field(None, description="Environment variables")
    cwd: str | None = Field(None, description="Working directory for the command")

    # HTTP configuration
    url: str | None = Field(None, description="URL for HTTP-based MCP server")

    @model_validator(mode="after")
    def validate_config(self):
        """Ensure either command or url is provided, but not both."""
        if not self.command and not self.url:
            raise ValueError("Either 'command' or 'url' must be provided")
        if self.command and self.url:
            raise ValueError("Cannot specify both 'command' and 'url'")
        return self


class MCPConfiguration(BaseModel):
    """Full MCP configuration structure."""

    mcpServers: dict[str, MCPServerConfig] = Field(default_factory=dict, description="MCP servers configuration")


def load_mcp_config() -> MCPConfiguration:
    """Load the current MCP configuration from Cursor's config file."""
    if not CURSOR_CONFIG_PATH.exists():
        # Create default config if it doesn't exist
        default_config = MCPConfiguration()
        save_mcp_config(default_config)
        return default_config

    with open(CURSOR_CONFIG_PATH) as f:
        data = json.load(f)

    return MCPConfiguration(**data)


def save_mcp_config(config: MCPConfiguration) -> None:
    """Save the MCP configuration to Cursor's config file."""
    # Ensure the directory exists
    CURSOR_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CURSOR_CONFIG_PATH, "w") as f:
        json.dump(config.model_dump(exclude_none=True), f, indent=2)


def defer_config_update(update_script: str) -> None:
    """Execute a config update script in a subprocess to avoid disconnection.

    This helper function spawns a detached subprocess that will modify the
    mcp.json file after the current function returns, preventing the connection
    from being severed mid-operation.

    Args:
        update_script: Python script content to execute for config update
    """
    import subprocess
    import sys
    import tempfile

    # Write the script to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(update_script)
        script_path = f.name

    # Launch the subprocess that will run after we return
    if sys.platform == "win32":
        # On Windows, use DETACHED_PROCESS to run independently
        subprocess.Popen(
            [sys.executable, script_path], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        )
    else:
        # On Unix, use nohup or similar
        subprocess.Popen([sys.executable, script_path])


@mcp.tool()
async def list_mcp_servers() -> str:
    """List all configured MCP servers in Cursor.

    Returns a formatted list of all MCP servers with their configurations.
    """
    config = load_mcp_config()

    if not config.mcpServers:
        return "No MCP servers configured."

    result = []
    for name, server in config.mcpServers.items():
        server_info = [
            f"**{name}**",
            f"  Command: {server.command}",
            f"  Args: {' '.join(server.args)}" if server.args else "  Args: (none)",
        ]
        if server.env:
            server_info.append(f"  Environment: {', '.join(f'{k}={v}' for k, v in server.env.items())}")
        result.append("\n".join(server_info))

    return "\n\n".join(result)


@mcp.tool()
async def add_mcp_server(
    name: str = Field(..., description="Unique name for the MCP server (e.g., 'weather', 'filesystem')"),
    command: str = Field(..., description="Command to execute the server (e.g., 'python', 'node', 'uv', 'docker')"),
    args: list[str] = Field(
        None,
        description="List of arguments for the command (e.g., ['run', 'server.py'] or ['--directory', '/path/to/server'])",
    ),
    env: dict[str, str] = Field(
        None, description="Optional environment variables as key-value pairs (e.g., {'API_KEY': 'your-key'})"
    ),
) -> str:
    """Add a new MCP server to Cursor configuration.

    Args:
        name: Unique name for the server
        command: Command to execute (e.g., 'python', 'node', 'uv')
        args: List of arguments for the command (e.g., ['run', 'server.py'])
        env: Optional environment variables as key-value pairs

    Returns:
        Success or error message
    """
    config = load_mcp_config()

    if name in config.mcpServers:
        return f"Error: Server '{name}' already exists. Use update_mcp_server to modify it."

    # Clear any existing logs for this server (in case it's being re-added)
    clear_server_logs(name)

    server_config = MCPServerConfig(command=command, args=args or [], env=env)

    # Create the update script
    server_dict = server_config.model_dump(exclude_none=True)
    update_script = f'''
import json
from pathlib import Path

config_path = r"{CURSOR_CONFIG_PATH}"

# Load current config
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Add the new server
config["mcpServers"]["{name}"] = {json.dumps(server_dict)}

# Save the updated config
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
'''

    # Defer the update to avoid disconnection
    defer_config_update(update_script)

    return f"Successfully initiated adding MCP server '{name}'. The server will be added in a moment."


@mcp.tool()
async def remove_mcp_server(
    name: str = Field(
        ...,
        description="Name of the MCP server to remove. WARNING: Do NOT remove 'cursor-manager' - it will kill this server!",
    ),
) -> str:
    """Remove an MCP server from Cursor configuration.

    WARNING: Removing the 'cursor-manager' server will cause this tool to stop working!

    Args:
        name: Name of the server to remove

    Returns:
        Success or error message
    """
    # Self-protection: prevent removing ourselves
    if name == "cursor-manager":
        return "WARNING: Cannot remove 'cursor-manager' - this would kill the current server! If you really need to remove it, do so manually in the mcp.json file."

    config = load_mcp_config()

    if name not in config.mcpServers:
        return f"Error: Server '{name}' not found."

    # Create the update script
    update_script = f'''
import json
from pathlib import Path

config_path = r"{CURSOR_CONFIG_PATH}"

# Load current config
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Remove the server
if "{name}" in config["mcpServers"]:
    del config["mcpServers"]["{name}"]

# Save the updated config
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
'''

    # Defer the update to avoid disconnection
    defer_config_update(update_script)

    return f"Successfully initiated removal of MCP server '{name}'. The server will be removed in a moment."


@mcp.tool()
async def update_mcp_server(
    name: str = Field(
        ..., description="Name of the MCP server to update. CAUTION: Be careful when updating 'cursor-manager'!"
    ),
    command: str | None = Field(None, description="New command to execute (optional, e.g., 'python', 'node')"),
    args: list[str] | None = Field(None, description="New list of arguments (optional, replaces all existing args)"),
    env: dict[str, str] | None = Field(
        None, description="Environment variables to add or update (optional, merged with existing)"
    ),
    clear_env: bool = Field(False, description="If True, removes all environment variables before applying new ones"),
) -> str:
    """Update an existing MCP server configuration.

    CAUTION: Updating the 'cursor-manager' server incorrectly may cause this tool to stop working!

    Args:
        name: Name of the server to update
        command: New command (optional)
        args: New arguments (optional)
        env: New environment variables (optional)
        clear_env: If True, clears all environment variables

    Returns:
        Success or error message
    """
    # Warning for self-modification
    if name == "cursor-manager":
        warning = "CAUTION: You are updating the 'cursor-manager' server. Incorrect changes may break this tool!\n"
    else:
        warning = ""

    config = load_mcp_config()

    if name not in config.mcpServers:
        return f"Error: Server '{name}' not found."

    # Clear logs when updating server configuration
    clear_server_logs(name)

    server = config.mcpServers[name]

    if command is not None:
        server.command = command

    if args is not None:
        server.args = args

    if clear_env:
        server.env = None
    elif env is not None:
        if server.env is None:
            server.env = env
        else:
            server.env.update(env)

    # Create the update script with the new configuration
    updated_server = config.mcpServers[name].model_dump(exclude_none=True)
    update_script = f'''
import json
from pathlib import Path

config_path = r"{CURSOR_CONFIG_PATH}"

# Load current config
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Update the server
config["mcpServers"]["{name}"] = {json.dumps(updated_server)}

# Save the updated config
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
'''

    # Defer the update to avoid disconnection
    defer_config_update(update_script)

    return f"{warning}Successfully initiated update of MCP server '{name}'. The server will be updated in a moment."


async def _kill_mcp_server_internal(name: str) -> str:
    """Internal function to kill/stop a running MCP server process.

    This is the actual implementation that can be called from other functions.

    Args:
        name: Name of the server to kill

    Returns:
        Status message
    """
    from .process_monitor import MCPProcessMonitor

    monitor = MCPProcessMonitor()
    processes = monitor.find_running_mcp_servers()

    killed = False
    for proc in processes:
        if proc.server_name == name and proc.pid:
            try:
                # Special handling for Docker containers
                if proc.name == "docker.exe" and "run" in proc.command:
                    # For Docker, we need to find the container ID
                    result = subprocess.run(
                        ["docker", "ps", "-q", "--filter", f"ancestor={name}"],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    if result.stdout.strip():
                        container_id = result.stdout.strip().split("\n")[0]
                        # Stop the container
                        subprocess.run(["docker", "stop", container_id], check=False, capture_output=True)
                        killed = True
                        return f"[OK] Stopped Docker container '{container_id}' for server '{name}'"
                    # Try to stop by name
                    subprocess.run(["docker", "stop", name], check=False, capture_output=True)
                    killed = True
                    return f"[OK] Attempted to stop Docker container '{name}'"

                # For regular processes, kill by PID
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], check=False, capture_output=True)
                else:
                    subprocess.run(["kill", "-9", str(proc.pid)], check=False, capture_output=True)

                killed = True
                return f"[OK] Killed server '{name}' (PID: {proc.pid})"

            except Exception as e:
                return f"[ERROR] Error killing server '{name}': {e}"

    if not killed:
        return f"[WARNING] Server '{name}' is not currently running."

    # This should never be reached, but satisfies the type checker
    return f"[ERROR] Unexpected state for server '{name}'"


@mcp.tool()
async def kill_mcp_server(name: str = Field(..., description="Name of the MCP server to kill/stop")) -> str:
    """Kill/stop a running MCP server process.

    This is useful for Docker-based servers that need to be stopped before refreshing
    to avoid port conflicts.

    Args:
        name: Name of the server to kill

    Returns:
        Status message
    """
    return await _kill_mcp_server_internal(name)


@mcp.tool()
async def refresh_mcp_server(
    name: str = Field(
        ...,
        description="Name of the MCP server to refresh/restart. WARNING: Refreshing 'cursor-manager' will disconnect this session!",
    ),
) -> str:
    """Restart a specific MCP server by toggling its configuration.

    WARNING: Refreshing the 'cursor-manager' server will disconnect the current session!

    This simulates the refresh behavior by temporarily removing and re-adding
    the server configuration, which forces Cursor to restart that specific server.

    Args:
        name: Name of the server to refresh

    Returns:
        Status message
    """
    # Warning for self-refresh
    if name == "cursor-manager":
        return "WARNING: Refreshing 'cursor-manager' will disconnect this session! The server will restart but you'll lose the current connection. If you really need to refresh it, use the Cursor UI instead."

    config = load_mcp_config()

    if name not in config.mcpServers:
        return f"Error: Server '{name}' not found."

    # Clear logs for this server since it's being refreshed
    handle_server_refresh(name)

    # First, kill any existing processes for this server
    from .process_monitor import MCPProcessMonitor

    monitor = MCPProcessMonitor()
    processes = monitor.find_running_mcp_servers()

    killed_processes = []

    # Kill any processes we can find for this server
    for proc in processes:
        if proc.server_name == name and proc.pid:
            try:
                # Use the internal kill function which properly handles Docker
                result = await _kill_mcp_server_internal(name)
                if "Killed" in result or "Stopped" in result:
                    killed_processes.append(f"Server '{name}' via kill_mcp_server")
                break  # kill_mcp_server handles all processes for this server

            except Exception as e:
                log_lifecycle("REFRESH_KILL_ERROR", f"Error killing {name}: {e}")

    # Add a small delay to ensure processes are truly dead
    if killed_processes:
        time.sleep(3)  # Increased from 1 to 3 seconds for Docker containers

    # The server configuration will be restored by the refresh script

    # Create the refresh script
    refresh_script = f'''
import json
import time
from pathlib import Path

config_path = r"{CURSOR_CONFIG_PATH}"
server_name = "{name}"

# Load config
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Save backup of the server config
server_backup = config["mcpServers"][server_name]

# Remove the server
del config["mcpServers"][server_name]
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)

# Wait for Cursor to detect the removal
time.sleep(7)  # Increased from 3 to 7 seconds for complex servers like Docker

# Re-add the server
config["mcpServers"][server_name] = server_backup
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
'''

    # Use the helper function to defer the update
    defer_config_update(refresh_script)

    # Build the response message
    if killed_processes:
        killed_msg = "Killed existing processes:\n" + "\n".join(f"  - {p}" for p in killed_processes) + "\n\n"
    else:
        killed_msg = ""

    return f"""Successfully initiated refresh of MCP server '{name}'.

{killed_msg}The server will be restarted in a moment by Cursor's automatic reconnection.

IMPORTANT: If '{name}' has new or updated tools, they will be available on your next message.
Simply send another message to see the updated tool list.

Note: All Cursor windows will reconnect to the new instance."""


@mcp.tool()
async def check_server_status(name: str = Field(..., description="Name of the MCP server to check status for")) -> str:
    """Check if an MCP server is currently running.

    Returns information about the server's process if it's running.

    Args:
        name: Name of the server to check

    Returns:
        Status information including PID if running
    """
    monitor = MCPProcessMonitor()
    status = monitor.get_server_status(name)

    if status["running"]:
        return f"""[OK] Server '{name}' is RUNNING
PID: {status["pid"]}
Process: {status["process_name"]}
Command: {status["command"][:100]}{"..." if len(status["command"]) > 100 else ""}"""
    return f"[ERROR] Server '{name}' is NOT RUNNING"


@mcp.tool()
async def list_running_servers() -> str:
    """List all currently running MCP servers.

    This tool scans system processes to find running MCP servers.

    Returns:
        List of running servers with their process information
    """
    monitor = MCPProcessMonitor()
    running = monitor.find_running_mcp_servers()

    if not running:
        return "No MCP servers are currently running."

    output = f"Found {len(running)} running MCP server(s):\n\n"

    for proc in running:
        output += f"* {proc.server_name or 'Unknown'}\n"
        output += f"   PID: {proc.pid}\n"
        output += f"   Process: {proc.name}\n"
        output += f"   Command: {proc.command[:80]}{'...' if len(proc.command) > 80 else ''}\n\n"

    return output.strip()


@mcp.tool()
async def get_server_logs(name: str = Field(..., description="Name of the MCP server to get logs for")) -> str:
    """Get actively collected logs from an MCP server.

    This tool returns logs that have been actively collected since the server started.
    Log collection begins automatically when a server process is detected.

    Args:
        name: Name of the server to get logs for

    Returns:
        Collected log output from the server (last 100 lines)
    """
    last_n = 100  # Default to last 100 lines

    # First check if server exists in config
    config = load_mcp_config()
    if name not in config.mcpServers:
        # Check if we have logs for it anyway (might be a recently removed server)
        collected_servers = get_all_collected_servers()
        if name not in collected_servers:
            return f"Error: Server '{name}' not found in configuration or collected logs."

    # Get collected logs
    logs = get_collected_logs(name, last_n)

    if "No logs collected" in logs:
        # Server might not have been detected yet, try to find it
        process_monitor = MCPProcessMonitor()
        status = process_monitor.get_server_status(name)

        if status["running"]:
            # Start collection now
            start_log_collection(name, status["pid"])
            return f"""Server '{name}' is running (PID: {status["pid"]})

Log collection has just been started. Please wait a moment and try again to see collected logs.

Tip: Logs are collected automatically when servers start. If you just started this server,
the logs should appear shortly."""
        return f"""Server '{name}' is not currently running.

No logs have been collected for this server. Logs are collected automatically when the server starts.

To see logs:
1. Start the server from Cursor's MCP settings
2. Wait a moment for log collection to begin
3. Run this command again"""

    # Return the collected logs
    output = f"Logs for server '{name}' (last {last_n} lines):\n"
    output += "=" * 60 + "\n"
    output += logs
    output += "\n" + "=" * 60

    # Add server status
    process_monitor = MCPProcessMonitor()
    status = process_monitor.get_server_status(name)
    if status["running"]:
        output += f"\n\n[OK] Server is currently RUNNING (PID: {status['pid']})"
    else:
        output += "\n\n[ERROR] Server is currently STOPPED"

    return output


def main():
    """Main entry point for the server."""
    import argparse
    import signal

    parser = argparse.ArgumentParser(description="Cursor MCP Manager")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server (default)")
    parser.add_argument("--stdio", action="store_true", help="Run as STDIO proxy")
    parser.add_argument(
        "--no-shutdown", action="store_true", help="Ignore shutdown signals (for background HTTP server)"
    )
    args = parser.parse_args()

    if args.stdio:
        # Run as STDIO proxy that connects to shared HTTP server
        import asyncio

        from .stdio_proxy import main as stdio_main

        asyncio.run(stdio_main())
    else:
        # Run as HTTP server (default)

        # If --no-shutdown is specified, ignore shutdown signals
        if args.no_shutdown:

            def signal_handler(signum, frame):
                log_lifecycle("SIGNAL_IGNORED", f"Ignoring signal {signum} - server running with --no-shutdown")

            # Ignore common shutdown signals
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            if hasattr(signal, "SIGHUP"):
                signal.signal(signal.SIGHUP, signal_handler)

        # Start log collection for any already running servers
        # Start the process watcher to continuously monitor for new processes
        try:
            watcher = get_process_watcher()
            watcher.start()
            log_lifecycle("PROCESS_WATCHER_STARTED", "Continuous process monitoring enabled")
        except Exception as e:
            log_lifecycle("PROCESS_WATCHER_ERROR", str(e))

        port = int(os.environ.get("CURSOR_MCP_PORT", 48765))
        host = "127.0.0.1"

        print(f"Starting Cursor MCP Manager HTTP server on {host}:{port}", file=sys.stderr)
        if args.no_shutdown:
            print(
                "Running in background mode (--no-shutdown). Use 'cursor-manager stop' to terminate.", file=sys.stderr
            )
        print("Configure in claude_desktop_config.json:", file=sys.stderr)
        print(f'  "cursor-manager": {{ "url": "http://{host}:{port}" }}', file=sys.stderr)

        mcp.run(transport="streamable-http", host=host, port=port)


if __name__ == "__main__":
    main()
