#!/usr/bin/env python3
"""
CLI tool for managing the cursor-mcp-manager HTTP server.

This provides commands to start, stop, and check status of the background HTTP server.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import click
import psutil

# Server configuration
HTTP_SERVER_HOST = "127.0.0.1"
# Use the same configurable port as the server
HTTP_SERVER_PORT = int(os.environ.get("CURSOR_MCP_PORT", 48765))
PID_FILE = Path.home() / ".cursor-mcp-manager" / "server.pid"


def get_server_pid():
    """Get the PID of the running HTTP server from the PID file."""
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except:
            return None
    return None


def is_server_running(pid=None):
    """Check if the HTTP server is running."""
    if pid is None:
        pid = get_server_pid()

    if pid is None:
        return False

    try:
        # Check if process exists
        process = psutil.Process(pid)

        # Verify it's our server by checking command line
        cmdline = " ".join(process.cmdline())
        if "cursor_mcp_manager" in cmdline and "--http" in cmdline:
            return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    return False


def save_server_pid(pid):
    """Save the server PID to file."""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(pid))


def remove_pid_file():
    """Remove the PID file."""
    if PID_FILE.exists():
        PID_FILE.unlink()


@click.group()
def cli():
    """Cursor MCP Manager - HTTP Server Management"""
    pass


@cli.command()
def start():
    """Start the HTTP server in the background."""
    # Check if already running
    if is_server_running():
        click.echo("[OK] HTTP server is already running")
        return

    click.echo("Starting HTTP server...")

    # Get the path to the current Python environment
    python_exe = sys.executable

    try:
        if sys.platform == "win32":
            # Windows: Use START command to run in background
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                [python_exe, "-m", "cursor_mcp_manager", "--http", "--no-shutdown"],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            # Unix: Use nohup
            process = subprocess.Popen(
                [python_exe, "-m", "cursor_mcp_manager", "--http", "--no-shutdown"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        # Save PID
        save_server_pid(process.pid)

        # Wait a moment and verify it started
        time.sleep(2)
        if is_server_running(process.pid):
            click.echo(f"[OK] HTTP server started successfully (PID: {process.pid})")
            click.echo(f"   Server URL: http://{HTTP_SERVER_HOST}:{HTTP_SERVER_PORT}")
        else:
            click.echo("[ERROR] Failed to start HTTP server")
            remove_pid_file()

    except Exception as e:
        click.echo(f"[ERROR] Error starting server: {e}")
        remove_pid_file()


@cli.command()
def stop():
    """Stop the running HTTP server."""
    pid = get_server_pid()

    if not is_server_running(pid):
        click.echo("[ERROR] HTTP server is not running")
        remove_pid_file()
        return

    click.echo(f"Stopping HTTP server (PID: {pid})...")

    try:
        process = psutil.Process(pid)

        # Try graceful termination first
        if sys.platform == "win32":
            process.terminate()
        else:
            os.kill(pid, signal.SIGTERM)

        # Wait for process to terminate
        try:
            process.wait(timeout=5)
        except psutil.TimeoutExpired:
            # Force kill if needed
            process.kill()
            process.wait()

        remove_pid_file()
        click.echo("[OK] HTTP server stopped successfully")

    except Exception as e:
        click.echo(f"[ERROR] Error stopping server: {e}")


@cli.command()
def status():
    """Check the status of the HTTP server."""
    pid = get_server_pid()

    if is_server_running(pid):
        try:
            process = psutil.Process(pid)
            create_time = process.create_time()
            uptime = time.time() - create_time

            # Format uptime
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)

            click.echo("[OK] HTTP server is running")
            click.echo(f"   PID: {pid}")
            click.echo(f"   URL: http://{HTTP_SERVER_HOST}:{HTTP_SERVER_PORT}")
            click.echo(f"   Uptime: {hours}h {minutes}m {seconds}s")

            # Try to get server info
            try:
                import httpx

                response = httpx.get(f"http://{HTTP_SERVER_HOST}:{HTTP_SERVER_PORT}/mcp/", timeout=2)
                if response.status_code == 200:
                    click.echo("   Health: Healthy [OK]")
                else:
                    click.echo(f"   Health: Unhealthy [WARNING] (status: {response.status_code})")
            except:
                click.echo("   Health: Not responding [ERROR]")

        except Exception as e:
            click.echo(f"[OK] HTTP server appears to be running (PID: {pid})")
            click.echo(f"   Unable to get detailed info: {e}")
    else:
        click.echo("[ERROR] HTTP server is not running")
        if PID_FILE.exists():
            click.echo("   (Stale PID file found, cleaning up...)")
            remove_pid_file()


@cli.command()
def restart():
    """Restart the HTTP server."""
    # Stop if running
    if is_server_running():
        stop.invoke(click.Context(stop))
        time.sleep(1)

    # Start
    start.invoke(click.Context(start))


@cli.command()
def logs():
    """Show the server logs."""
    log_file = Path.home() / ".cursor-mcp-manager" / "logs" / "http_server.log"

    if not log_file.exists():
        click.echo("[ERROR] No log file found")
        return

    # Show last 50 lines
    with open(log_file) as f:
        lines = f.readlines()
        recent_lines = lines[-50:] if len(lines) > 50 else lines

        click.echo("=== Recent Server Logs ===")
        for line in recent_lines:
            click.echo(line.rstrip())


if __name__ == "__main__":
    cli()
