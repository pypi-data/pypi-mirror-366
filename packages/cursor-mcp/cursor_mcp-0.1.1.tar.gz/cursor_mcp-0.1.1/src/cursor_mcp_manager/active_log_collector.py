"""Active log collection for MCP servers."""

import subprocess
import threading
import time
from collections import deque
from datetime import datetime

# Global log storage - server_name -> deque of log lines
SERVER_LOGS: dict[str, deque[str]] = {}
LOG_COLLECTORS: dict[str, threading.Thread] = {}
MAX_LOG_LINES = 1000  # Keep last 1000 lines per server


def log_line(server_name: str, line: str, source: str = "STDOUT"):
    """Add a log line to the server's log buffer."""
    if server_name not in SERVER_LOGS:
        SERVER_LOGS[server_name] = deque(maxlen=MAX_LOG_LINES)

    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    SERVER_LOGS[server_name].append(f"[{timestamp}] [{source}] {line}")


def start_log_collection(server_name: str, pid: str):
    """Start collecting logs for a server process."""
    if server_name in LOG_COLLECTORS and LOG_COLLECTORS[server_name].is_alive():
        return  # Already collecting

    # Clear old logs when starting fresh
    SERVER_LOGS[server_name] = deque(maxlen=MAX_LOG_LINES)
    log_line(server_name, f"=== Log collection started for PID {pid} ===", "SYSTEM")

    def collect_logs():
        """Thread function to collect logs from a process."""
        try:
            # On Windows, we can try to capture output using wmic and handle redirection
            # For docker containers, we use docker logs -f
            if "gmail" in server_name.lower():
                # Special handling for docker containers
                # First, find the container ID
                result = subprocess.run(
                    ["docker", "ps", "--filter", "ancestor=gmail-clone", "--format", "{{.ID}}"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                container_id = result.stdout.strip()

                if container_id:
                    log_line(server_name, f"Found Docker container: {container_id}", "SYSTEM")
                    # Follow logs
                    proc = subprocess.Popen(
                        ["docker", "logs", "-f", container_id],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                    )

                    # Read both stdout and stderr
                    def read_stream(stream, source):
                        try:
                            for line in stream:
                                if line.strip():
                                    log_line(server_name, line.strip(), source)
                        except:
                            pass

                    stdout_thread = threading.Thread(target=read_stream, args=(proc.stdout, "STDOUT"))
                    stderr_thread = threading.Thread(target=read_stream, args=(proc.stderr, "STDERR"))
                    stdout_thread.daemon = True
                    stderr_thread.daemon = True
                    stdout_thread.start()
                    stderr_thread.start()

                    # Wait for process to end
                    proc.wait()
                    log_line(server_name, "Docker container stopped", "SYSTEM")
                else:
                    log_line(server_name, "Could not find Docker container", "ERROR")

            else:
                # For regular processes, we'll monitor using different approach
                # Since we can't easily attach to an already running process's streams on Windows,
                # we'll at least log that we're monitoring
                log_line(server_name, f"Monitoring process PID {pid}", "SYSTEM")

                # Poll process status
                while True:
                    # Check if process still exists
                    result = subprocess.run(
                        f'wmic process where "processid={pid}" get processid 2>nul',
                        check=False,
                        shell=True,
                        capture_output=True,
                        text=True,
                    )
                    if pid not in result.stdout:
                        log_line(server_name, f"Process PID {pid} has terminated", "SYSTEM")
                        break
                    time.sleep(5)  # Check every 5 seconds

        except Exception as e:
            log_line(server_name, f"Log collection error: {e}", "ERROR")
        finally:
            log_line(server_name, "=== Log collection stopped ===", "SYSTEM")

    # Start collection thread
    thread = threading.Thread(target=collect_logs, daemon=True)
    thread.start()
    LOG_COLLECTORS[server_name] = thread


def get_server_logs(server_name: str, last_n: int | None = None) -> str:
    """Get collected logs for a server."""
    if server_name not in SERVER_LOGS:
        return f"No logs collected for server '{server_name}'"

    logs = list(SERVER_LOGS[server_name])
    if last_n and last_n < len(logs):
        logs = logs[-last_n:]

    if not logs:
        return f"No logs available for server '{server_name}' (collection may be starting)"

    return "\n".join(logs)


def get_all_collected_servers() -> list:
    """Get list of all servers with collected logs."""
    return list(SERVER_LOGS.keys())


def clear_server_logs(server_name: str):
    """Clear logs for a specific server."""
    # Stop any active log collection thread
    # The thread will naturally stop when it detects the process is gone
    # We just remove it from our tracking
    LOG_COLLECTORS.pop(server_name, None)

    # Clear the logs
    if server_name in SERVER_LOGS:
        SERVER_LOGS[server_name].clear()
        log_line(server_name, "=== Logs cleared ===", "SYSTEM")
