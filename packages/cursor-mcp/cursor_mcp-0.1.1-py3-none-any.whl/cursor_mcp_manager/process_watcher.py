"""Continuous process watcher for MCP servers."""

import threading
import time
from collections import defaultdict

from .active_log_collector import clear_server_logs, start_log_collection
from .process_monitor import MCPProcessMonitor


class ProcessWatcher:
    """Continuously watches for new MCP processes and manages log collection."""

    def __init__(self):
        self.monitor = MCPProcessMonitor()
        self.tracked_processes: set[tuple] = set()  # (server_name, pid) tuples
        self.running = False
        self.watch_thread = None
        # Track processes that started recently to detect races
        self.recent_starts: dict[str, list[tuple]] = defaultdict(list)  # server_name -> [(pid, timestamp)]
        self.race_detection_window = 3.0  # seconds

    def start(self):
        """Start the process watcher."""
        if self.running:
            return

        self.running = True
        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()

    def stop(self):
        """Stop the process watcher."""
        self.running = False
        if self.watch_thread:
            self.watch_thread.join(timeout=5)

    def _watch_loop(self):
        """Main watch loop that runs continuously."""
        while self.running:
            try:
                # Refresh known commands to catch newly added servers
                self.monitor.refresh_known_commands()
                
                # Find all running MCP processes
                processes = self.monitor.find_running_mcp_servers()
                current_time = time.time()

                # Clean up old entries from recent_starts
                for server_name in list(self.recent_starts.keys()):
                    self.recent_starts[server_name] = [
                        (pid, ts)
                        for pid, ts in self.recent_starts[server_name]
                        if current_time - ts < self.race_detection_window * 2
                    ]
                    if not self.recent_starts[server_name]:
                        del self.recent_starts[server_name]

                current_processes = set()
                for proc in processes:
                    if proc.server_name and proc.pid:
                        process_key = (proc.server_name, proc.pid)
                        current_processes.add(process_key)

                        # Check if this is a new process we haven't tracked
                        if process_key not in self.tracked_processes:
                            # New process detected!
                            print(f"[ProcessWatcher] New process detected: {proc.server_name} (PID: {proc.pid})")

                            # Add to recent starts
                            self.recent_starts[proc.server_name].append((proc.pid, current_time))

                            # Check if we're in a race condition
                            recent_pids = [
                                pid
                                for pid, ts in self.recent_starts[proc.server_name]
                                if current_time - ts < self.race_detection_window
                            ]

                            if len(recent_pids) > 1:
                                # Multiple processes started recently - likely a race
                                print(
                                    f"[ProcessWatcher] Detected race condition for {proc.server_name} ({len(recent_pids)} processes). Deferring log collection..."
                                )
                                # Don't start log collection yet - wait for the winner
                            else:
                                # Single process or first in a potential race
                                start_log_collection(proc.server_name, str(proc.pid))

                # Check for race resolution
                for server_name in list(self.recent_starts.keys()):
                    recent_entries = [
                        (pid, ts)
                        for pid, ts in self.recent_starts[server_name]
                        if current_time - ts < self.race_detection_window
                    ]

                    if len(recent_entries) > 1:
                        # Multiple processes started recently
                        recent_pids = [pid for pid, ts in recent_entries]
                        alive_pids = [pid for sn, pid in current_processes if sn == server_name and pid in recent_pids]

                        if len(alive_pids) == 1:
                            # Race resolved! Only one survivor
                            winner_pid = alive_pids[0]
                            # winner_key = (server_name, winner_pid)  # Not used

                            # Check if we already started log collection for any of the racing processes
                            from .active_log_collector import LOG_COLLECTORS

                            if server_name not in LOG_COLLECTORS:
                                print(
                                    f"[ProcessWatcher] Race resolved for {server_name}. Winner: PID {winner_pid}. Starting log collection..."
                                )
                                start_log_collection(server_name, str(winner_pid))

                            # Clean up recent_starts for this server
                            self.recent_starts[server_name] = [(winner_pid, current_time)]

                # Check for processes that have disappeared
                disappeared = self.tracked_processes - current_processes
                for server_name, pid in disappeared:
                    print(f"[ProcessWatcher] Process disappeared: {server_name} (PID: {pid})")
                    # Note: log collection thread will detect this and stop itself

                # Update tracked processes
                self.tracked_processes = current_processes

            except Exception as e:
                print(f"[ProcessWatcher] Error in watch loop: {e}")

            # Sleep before next check
            time.sleep(3)  # Check every 3 seconds


# Global instance
_process_watcher = None


def get_process_watcher() -> ProcessWatcher:
    """Get the global process watcher instance."""
    global _process_watcher
    if _process_watcher is None:
        _process_watcher = ProcessWatcher()
    return _process_watcher


def handle_server_refresh(server_name: str):
    """Handle when a server is being refreshed - clear its logs."""
    print(f"[ProcessWatcher] Clearing logs for refreshed server: {server_name}")
    clear_server_logs(server_name)

    # Remove from tracked processes so it gets re-detected
    watcher = get_process_watcher()
    watcher.tracked_processes = {(name, pid) for name, pid in watcher.tracked_processes if name != server_name}
