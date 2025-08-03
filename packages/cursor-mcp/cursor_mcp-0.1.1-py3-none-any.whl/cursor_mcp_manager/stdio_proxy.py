#!/usr/bin/env python3
"""
STDIO proxy for cursor-mcp-manager.

This acts as a thin STDIO-to-HTTP bridge that connects to the shared HTTP server.
It properly handles the MCP protocol over STDIO transport.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx

# Configure logging to file only (not stderr which would interfere with STDIO)
log_dir = Path.home() / ".cursor-mcp-manager" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_dir / "stdio_proxy.log")],
)
logger = logging.getLogger(__name__)

# HTTP server configuration
# You can set CURSOR_MCP_PORT environment variable to override
HTTP_SERVER_PORT = int(os.environ.get("CURSOR_MCP_PORT", 48765))
HTTP_SERVER_HOST = "127.0.0.1"
HTTP_SERVER_URL = f"http://{HTTP_SERVER_HOST}:{HTTP_SERVER_PORT}"


class StdioToHttpBridge:
    """Bridges STDIO MCP messages to HTTP server using SSE."""

    def __init__(self):
        self.client: httpx.AsyncClient | None = None
        self.session_id: str | None = None
        self.running = True

    async def start(self):
        """Start the bridge."""
        logger.info("=== STDIO Bridge Starting ===")
        self.client = httpx.AsyncClient(timeout=30.0)

        # Ensure HTTP server is running
        logger.info("Checking/starting HTTP server...")
        await self.ensure_http_server_running()
        logger.info("HTTP server ready, starting message processing")

        # Initialize session
        await self.initialize_session()

        try:
            # Only need to read from stdin and forward
            # Responses come back synchronously in streamable-HTTP
            await self.read_stdin_and_forward()
        finally:
            # Clean shutdown
            await self.cleanup()

    async def ensure_http_server_running(self):
        """Ensure the HTTP server is running, start it if not."""
        max_retries = 15
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                # Check if server is running by making a simple request
                # The /mcp/ endpoint expects proper headers, so we'll just check if the port is open
                response = await self.client.get(f"{HTTP_SERVER_URL}/")
                # Any response means the server is running
                logger.info(f"HTTP server check: status {response.status_code}")
                if response.status_code:  # Any status code means it's running
                    logger.info("HTTP server is already running")
                    return
            except Exception as e:
                logger.info(f"HTTP server not reachable (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt == 0:
                    # Try to start the HTTP server
                    logger.info("Attempting to start HTTP server...")
                    try:
                        # Get the path to the current Python environment
                        # Use the same Python that's running this script
                        python_exe = sys.executable

                        if sys.platform == "win32":
                            # Windows: Use START command to run in background
                            startupinfo = subprocess.STARTUPINFO()
                            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            startupinfo.wShowWindow = subprocess.SW_HIDE

                            # Log the command we're running
                            cmd = [python_exe, "-m", "cursor_mcp_manager", "--http", "--no-shutdown"]
                            logger.info(f"Starting HTTP server with command: {' '.join(cmd)}")

                            # Create log files for subprocess output
                            log_dir = Path.home() / ".cursor-mcp-manager" / "logs"
                            log_dir.mkdir(parents=True, exist_ok=True)

                            # Note: We don't use pythonw.exe because it might not work properly with modules
                            logger.info(f"Using python.exe: {python_exe}")

                            with (
                                open(log_dir / "http_server_stdout.log", "w") as stdout_log,
                                open(log_dir / "http_server_stderr.log", "w") as stderr_log,
                            ):
                                process = subprocess.Popen(
                                    cmd,
                                    startupinfo=startupinfo,
                                    creationflags=subprocess.CREATE_NO_WINDOW
                                    | subprocess.CREATE_NEW_PROCESS_GROUP
                                    | subprocess.DETACHED_PROCESS,
                                    stdout=stdout_log,
                                    stderr=stderr_log,
                                    cwd=Path(__file__).parent.parent.parent,  # Set working directory to project root
                                )

                            # Save PID for management
                            pid_file = Path.home() / ".cursor-mcp-manager" / "server.pid"
                            pid_file.parent.mkdir(parents=True, exist_ok=True)
                            pid_file.write_text(str(process.pid))
                        else:
                            # Unix: Use nohup
                            cmd = [python_exe, "-m", "cursor_mcp_manager", "--http", "--no-shutdown"]
                            logger.info(f"Starting HTTP server with command: {' '.join(cmd)}")

                            # Create log files for subprocess output
                            log_dir = Path.home() / ".cursor-mcp-manager" / "logs"
                            log_dir.mkdir(parents=True, exist_ok=True)

                            with (
                                open(log_dir / "http_server_stdout.log", "w") as stdout_log,
                                open(log_dir / "http_server_stderr.log", "w") as stderr_log,
                            ):
                                process = subprocess.Popen(
                                    cmd,
                                    stdout=stdout_log,
                                    stderr=stderr_log,
                                    start_new_session=True,
                                    cwd=Path(__file__).parent.parent.parent,  # Set working directory to project root
                                )

                            # Save PID for management
                            pid_file = Path.home() / ".cursor-mcp-manager" / "server.pid"
                            pid_file.parent.mkdir(parents=True, exist_ok=True)
                            pid_file.write_text(str(process.pid))

                        logger.info(f"HTTP server started with PID: {process.pid}")

                        # Give FastMCP more time to fully initialize
                        logger.info("Waiting for HTTP server to be ready...")
                        await asyncio.sleep(5)

                        # Verify the server is actually responding
                        server_ready = False
                        for i in range(10):
                            try:
                                test_response = await self.client.get(f"{HTTP_SERVER_URL}/health", timeout=2.0)
                                if test_response.status_code in [200, 404]:  # 404 is OK, means server is up
                                    server_ready = True
                                    logger.info("HTTP server is responding to requests")
                                    break
                            except:
                                pass

                            if i < 9:
                                logger.info(f"Waiting for server to respond... ({i + 1}/10)")
                                await asyncio.sleep(1)

                        if not server_ready:
                            logger.warning("HTTP server may not be fully ready yet")

                        # Check if process is still running
                        poll_result = process.poll()
                        if poll_result is not None:
                            # Process exited, check logs
                            logger.error(f"HTTP server process exited with code: {poll_result}")
                            try:
                                with open(log_dir / "http_server_stderr.log") as f:
                                    stderr_content = f.read()
                                if stderr_content:
                                    logger.error(f"HTTP server stderr: {stderr_content}")
                                with open(log_dir / "http_server_stdout.log") as f:
                                    stdout_content = f.read()
                                if stdout_content:
                                    logger.error(f"HTTP server stdout: {stdout_content}")
                            except Exception as e:
                                logger.error(f"Couldn't read server logs: {e}")

                            # Try running the command directly to capture error
                            try:
                                result = subprocess.run(
                                    cmd,
                                    check=False,
                                    capture_output=True,
                                    text=True,
                                    cwd=Path(__file__).parent.parent.parent,
                                )
                                if result.stderr:
                                    logger.error(f"Direct run stderr: {result.stderr}")
                                if result.stdout:
                                    logger.error(f"Direct run stdout: {result.stdout}")
                            except Exception as e:
                                logger.error(f"Direct run failed: {e}")
                    except Exception as e:
                        logger.error(f"Failed to start HTTP server: {e}")

                await asyncio.sleep(retry_delay)

        raise RuntimeError("Could not connect to or start HTTP server")

    async def initialize_session(self):
        """Initialize session with the HTTP server using streamable-HTTP transport."""
        # For streamable-HTTP, we don't need a separate initialization
        # The session ID will be assigned by the server on the first request
        self.session_id = None
        logger.info("Ready to forward requests to HTTP server")

    async def read_stdin_and_forward(self):
        """Read JSON-RPC messages from stdin and forward to HTTP server."""
        logger.info("=== Starting stdin reader ===")
        if sys.platform == "win32":
            # Windows-specific handling to avoid asyncio issues
            import queue
            import threading

            q = queue.Queue()

            def read_stdin_thread():
                while self.running:
                    try:
                        line = sys.stdin.readline()
                        if not line:
                            break
                        q.put(line)
                    except Exception as e:
                        logger.error(f"Error reading stdin in thread: {e}")
                        break

            thread = threading.Thread(target=read_stdin_thread, daemon=True)
            thread.start()

            buffer = ""
            while self.running:
                try:
                    # Non-blocking read with timeout
                    try:
                        line = q.get(timeout=0.1)
                        buffer += line
                    except queue.Empty:
                        continue

                    # Process complete lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()

                        if not line:
                            continue

                        try:
                            message = json.loads(line)
                            logger.info(
                                f"[STDIN] Received message: method={message.get('method', 'N/A')}, id={message.get('id', 'N/A')}"
                            )

                            # Handle MCP lifecycle messages
                            method = message.get("method", "")

                            # Special handling for shutdown/exit
                            if method in ["shutdown", "exit", "notifications/exit"]:
                                logger.info(f"Received {method} - shutting down STDIO proxy")
                                # Forward to HTTP server but don't stop it
                                await self.client.post(
                                    f"{HTTP_SERVER_URL}/mcp/",
                                    json=message,
                                    headers={"Content-Type": "application/json", "mcp-session-id": self.session_id},
                                )
                                # Stop the STDIO proxy only
                                self.running = False
                                break

                            # Forward to HTTP server
                            headers = {
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/event-stream",
                            }
                            if self.session_id:
                                headers["mcp-session-id"] = self.session_id

                            response = await self.client.post(f"{HTTP_SERVER_URL}/mcp/", json=message, headers=headers)

                            # Extract session ID from response headers if not set
                            if not self.session_id:
                                # Try both possible header names
                                if "mcp-session-id" in response.headers:
                                    self.session_id = response.headers["mcp-session-id"]
                                    logger.info(f"Received session ID from mcp-session-id: {self.session_id}")
                                elif "X-Session-Id" in response.headers:
                                    self.session_id = response.headers["X-Session-Id"]
                                    logger.info(f"Received session ID from X-Session-Id: {self.session_id}")

                            if response.status_code == 200:
                                # Check if response is SSE (Server-Sent Events)
                                content_type = response.headers.get("content-type", "")
                                logger.info(f"[HTTP] Response received: status=200, content-type={content_type}")
                                if "text/event-stream" in content_type:
                                    # Parse SSE format
                                    text = response.text
                                    logger.info(f"[SSE] Response length: {len(text)}, content: {text[:200]!r}")
                                    found_data = False
                                    for line in text.strip().split("\n"):
                                        if line.startswith("data: "):
                                            try:
                                                data = json.loads(line[6:])  # Skip "data: " prefix
                                                logger.debug(f"Got SSE response: {data}")
                                                self.write_to_stdout(data)
                                                found_data = True
                                            except json.JSONDecodeError as e:
                                                logger.error(f"Failed to parse SSE data: {e} - Line: {line!r}")
                                    if not found_data:
                                        logger.error("No valid data found in SSE response")
                                else:
                                    # Regular JSON response
                                    result = response.json()
                                    logger.debug(f"Got immediate response: {result}")
                                    self.write_to_stdout(result)
                            else:
                                # Log error response
                                logger.error(f"HTTP error {response.status_code}: {response.text}")
                                try:
                                    error_data = response.json()
                                    logger.error(f"Error details: {error_data}")
                                except Exception as e:
                                    logger.error(f"Error details: {response.text} - {e}")
                                    pass

                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON from stdin: {e} - Line: {line}")
                            # Send JSON-RPC parse error if we can identify a request
                            error_response = {
                                "jsonrpc": "2.0",
                                "error": {"code": -32700, "message": "Parse error", "data": str(e)},
                            }
                            self.write_to_stdout(error_response)
                        except Exception as e:
                            logger.error(f"Error forwarding message: {e}")
                            # Send internal error if this was a request with an ID
                            if isinstance(message, dict) and "id" in message:
                                error_response = {
                                    "jsonrpc": "2.0",
                                    "id": message["id"],
                                    "error": {"code": -32603, "message": "Internal error", "data": str(e)},
                                }
                                self.write_to_stdout(error_response)

                except Exception as e:
                    logger.error(f"Error reading stdin: {e}")
                    break
        else:
            # Unix/Linux/Mac - use asyncio stdin reading
            reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(reader)
            loop = asyncio.get_event_loop()

            await loop.connect_read_pipe(lambda: protocol, sys.stdin)

            buffer = ""
            while self.running:
                try:
                    # Read data from stdin
                    data = await reader.read(4096)
                    if not data:
                        break

                    buffer += data.decode("utf-8", errors="replace")

                    # Process complete lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()

                        if not line:
                            continue

                        try:
                            message = json.loads(line)
                            logger.info(
                                f"[STDIN] Received message: method={message.get('method', 'N/A')}, id={message.get('id', 'N/A')}"
                            )

                            # Handle MCP lifecycle messages
                            method = message.get("method", "")

                            # Special handling for shutdown/exit
                            if method in ["shutdown", "exit", "notifications/exit"]:
                                logger.info(f"Received {method} - shutting down STDIO proxy")
                                # Forward to HTTP server but don't stop it
                                await self.client.post(
                                    f"{HTTP_SERVER_URL}/mcp/",
                                    json=message,
                                    headers={"Content-Type": "application/json", "mcp-session-id": self.session_id},
                                )
                                # Stop the STDIO proxy only
                                self.running = False
                                break

                            # Forward to HTTP server
                            headers = {
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/event-stream",
                            }
                            if self.session_id:
                                headers["mcp-session-id"] = self.session_id

                            response = await self.client.post(f"{HTTP_SERVER_URL}/mcp/", json=message, headers=headers)

                            # Extract session ID from response headers if not set
                            if not self.session_id:
                                # Try both possible header names
                                if "mcp-session-id" in response.headers:
                                    self.session_id = response.headers["mcp-session-id"]
                                    logger.info(f"Received session ID from mcp-session-id: {self.session_id}")
                                elif "X-Session-Id" in response.headers:
                                    self.session_id = response.headers["X-Session-Id"]
                                    logger.info(f"Received session ID from X-Session-Id: {self.session_id}")

                            if response.status_code == 200:
                                # Check if response is SSE (Server-Sent Events)
                                content_type = response.headers.get("content-type", "")
                                logger.info(f"[HTTP] Response received: status=200, content-type={content_type}")
                                if "text/event-stream" in content_type:
                                    # Parse SSE format
                                    text = response.text
                                    logger.info(f"[SSE] Response length: {len(text)}, content: {text[:200]!r}")
                                    found_data = False
                                    for line in text.strip().split("\n"):
                                        if line.startswith("data: "):
                                            try:
                                                data = json.loads(line[6:])  # Skip "data: " prefix
                                                logger.debug(f"Got SSE response: {data}")
                                                self.write_to_stdout(data)
                                                found_data = True
                                            except json.JSONDecodeError as e:
                                                logger.error(f"Failed to parse SSE data: {e} - Line: {line!r}")
                                    if not found_data:
                                        logger.error("No valid data found in SSE response")
                                else:
                                    # Regular JSON response
                                    result = response.json()
                                    logger.debug(f"Got immediate response: {result}")
                                    self.write_to_stdout(result)
                            else:
                                # Log error response
                                logger.error(f"HTTP error {response.status_code}: {response.text}")
                                try:
                                    error_data = response.json()
                                    logger.error(f"Error details: {error_data}")
                                except Exception as e:
                                    logger.error(f"Error details: {response.text} - {e}")
                                    pass

                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON from stdin: {e} - Line: {line}")
                            # Send JSON-RPC parse error if we can identify a request
                            error_response = {
                                "jsonrpc": "2.0",
                                "error": {"code": -32700, "message": "Parse error", "data": str(e)},
                            }
                            self.write_to_stdout(error_response)
                        except Exception as e:
                            logger.error(f"Error forwarding message: {e}")
                            # Send internal error if this was a request with an ID
                            if isinstance(message, dict) and "id" in message:
                                error_response = {
                                    "jsonrpc": "2.0",
                                    "id": message["id"],
                                    "error": {"code": -32603, "message": "Internal error", "data": str(e)},
                                }
                                self.write_to_stdout(error_response)

                except Exception as e:
                    logger.error(f"Error reading stdin: {e}")
                    break

    async def poll_for_notifications(self):
        """Poll for server-initiated notifications (not used in streamable-HTTP)."""
        # In streamable-HTTP, server notifications are sent as responses to client requests
        # No separate polling mechanism is needed
        pass

    def write_to_stdout(self, message: dict[str, Any]):
        """Write a message to stdout."""
        try:
            output = json.dumps(message, separators=(",", ":")) + "\n"
            sys.stdout.write(output)
            sys.stdout.flush()
            logger.debug(f"Wrote to stdout: {message}")
        except Exception as e:
            logger.error(f"Error writing to stdout: {e}")

    async def cleanup(self):
        """Clean up resources and connections."""
        logger.info("Cleaning up STDIO proxy...")
        self.running = False

        # Close HTTP client
        if self.client:
            try:
                await self.client.aclose()
            except Exception as e:
                logger.error(f"Error closing HTTP client: {e}")

        # Note: We intentionally do NOT stop the HTTP server here
        # It should continue running for other STDIO connections
        logger.info("STDIO proxy cleanup complete")


async def main():
    """Main entry point for STDIO proxy."""
    bridge = StdioToHttpBridge()

    try:
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        # Send error to stdout
        error_response = {"jsonrpc": "2.0", "error": {"code": -32603, "message": f"Bridge error: {e!s}"}}
        print(json.dumps(error_response))
        sys.stdout.flush()
    finally:
        await bridge.cleanup()


def run_stdio_server():
    """Entry point for the stdio server command."""
    # Ensure stdout is in binary mode on Windows
    if sys.platform == "win32":
        import msvcrt

        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)

    asyncio.run(main())


if __name__ == "__main__":
    run_stdio_server()
