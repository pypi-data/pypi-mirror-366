"""Process monitoring utilities for MCP servers."""

import subprocess
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MCPProcess:
    """Represents a running MCP server process."""

    pid: str
    ppid: str
    name: str
    command: str
    server_name: str | None = None
    started_at: datetime | None = None


class MCPProcessMonitor:
    """Monitor running MCP server processes."""

    def __init__(self):
        self.known_commands = self._load_known_commands()
    
    def refresh_known_commands(self):
        """Refresh the known commands from the current mcp.json config."""
        self.known_commands = self._load_known_commands()

    def _load_known_commands(self) -> dict[str, str]:
        """Load MCP server commands from mcp.json."""
        from .server import load_mcp_config

        config = load_mcp_config()
        commands = {}

        for server_name, server_config in config.mcpServers.items():
            # Skip HTTP-based servers
            if server_config.url:
                continue

            # Build the command string for STDIO servers
            cmd = server_config.command
            args = server_config.args if server_config.args else []

            # Create identifiable patterns
            if cmd == "docker":
                # For docker, look for unique container name
                if "gmail-clone" in str(args):
                    commands["gmail-clone"] = server_name
                elif any("gmail" in arg for arg in args):
                    commands["gmail"] = server_name
            elif cmd == "uv":
                # For uv, look for the package name
                for arg in args:
                    if "cursor-mcp-manager" in arg:
                        commands["cursor-mcp-manager"] = server_name
                    elif "browser-mcp" in arg:
                        commands["browser-mcp"] = server_name
            elif cmd == "python":
                # For python scripts, look for script name
                for arg in args:
                    if ".py" in arg:
                        script_name = arg.split("\\")[-1].split("/")[-1]
                        commands[script_name] = server_name

        return commands

    def find_running_mcp_servers(self) -> list[MCPProcess]:
        """Find all running MCP server processes."""
        processes = []

        try:
            # Get all processes
            cmd = "wmic process get processid,parentprocessid,name,commandline /format:csv"
            result = subprocess.run(cmd, check=False, shell=True, capture_output=True, text=True)

            for line in result.stdout.strip().split("\n")[2:]:  # Skip headers
                if not line.strip():
                    continue

                try:
                    parts = line.split(",", 4)
                    if len(parts) >= 5:
                        # computer = parts[0]  # Not used
                        cmdline = parts[1]
                        name = parts[2]
                        ppid = parts[3]
                        pid = parts[4]

                        # Check if this might be an MCP server
                        server_name = self._identify_mcp_server(name, cmdline)
                        if server_name:
                            proc = MCPProcess(pid=pid, ppid=ppid, name=name, command=cmdline, server_name=server_name)
                            processes.append(proc)
                except:
                    pass

        except Exception:
            pass

        return processes

    def _identify_mcp_server(self, process_name: str, cmdline: str) -> str | None:
        """Identify if a process is an MCP server and return its name."""
        cmdline_lower = cmdline.lower()

        # Check against known patterns from mcp.json config only
        for pattern, server_name in self.known_commands.items():
            if pattern.lower() in cmdline_lower:
                return server_name

        # Only return servers that are explicitly configured in mcp.json
        # This prevents logging of unrelated MCP processes
        return None

    def get_server_status(self, server_name: str) -> dict[str, any]:
        """Get status of a specific MCP server."""
        running_servers = self.find_running_mcp_servers()

        for proc in running_servers:
            if proc.server_name == server_name:
                return {"running": True, "pid": proc.pid, "process_name": proc.name, "command": proc.command}

        return {"running": False, "pid": None, "process_name": None, "command": None}
