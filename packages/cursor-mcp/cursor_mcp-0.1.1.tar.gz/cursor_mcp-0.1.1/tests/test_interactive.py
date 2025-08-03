#!/usr/bin/env python3
"""
Interactive test script for MCP STDIO proxy.
Allows manual sending of JSON-RPC messages to test the server.
"""

import json
import subprocess
import sys
import threading
import time


class InteractiveTester:
    def __init__(self):
        self.process = None
        self.running = True

    def start_server(self):
        """Start the MCP server."""
        print("Starting MCP server...")
        cmd = [sys.executable, "-m", "cursor_mcp_manager", "--stdio"]

        self.process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=0
        )

        # Start output readers
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

        print("Server started. Type 'help' for commands.\n")

    def _read_stdout(self):
        """Read stdout from server."""
        while self.running and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    print(f"📥 Server: {line.strip()}")
            except:
                break

    def _read_stderr(self):
        """Read stderr from server."""
        while self.running and self.process.poll() is None:
            try:
                line = self.process.stderr.readline()
                if line:
                    print(f"📝 Log: {line.strip()}")
            except:
                break

    def send_json(self, message):
        """Send JSON message to server."""
        try:
            msg_str = json.dumps(message)
            print(f"📤 Sending: {msg_str}")
            self.process.stdin.write(msg_str + "\n")
            self.process.stdin.flush()
        except Exception as e:
            print(f"❌ Error: {e}")

    def run_interactive(self):
        """Run interactive loop."""
        # Pre-defined messages
        messages = {
            "init": {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "InteractiveTest", "version": "1.0.0"},
                },
            },
            "initialized": {"jsonrpc": "2.0", "method": "notifications/initialized"},
            "list_tools": {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            "status": {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "get_mcp_servers_status", "arguments": {}},
            },
            "list_servers": {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "list_mcp_servers", "arguments": {}},
            },
            "exit": {"jsonrpc": "2.0", "method": "notifications/exit"},
        }

        print("\nAvailable commands:")
        print("  init        - Send initialize request")
        print("  initialized - Send initialized notification")
        print("  list_tools  - List available tools")
        print("  status      - Get server status")
        print("  list_servers- List MCP servers")
        print("  exit        - Send exit notification")
        print("  quit        - Quit this tester")
        print("  json <msg>  - Send custom JSON message")
        print("\n")

        while self.running:
            try:
                cmd = input(">>> ").strip()

                if cmd == "quit":
                    break
                if cmd in messages:
                    self.send_json(messages[cmd])
                elif cmd.startswith("json "):
                    try:
                        custom_msg = json.loads(cmd[5:])
                        self.send_json(custom_msg)
                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON: {e}")
                elif cmd == "help":
                    print(
                        "Available commands: init, initialized, list_tools, status, list_servers, exit, quit, json <msg>"
                    )
                else:
                    print("Unknown command. Type 'help' for available commands.")

                # Give server time to respond
                time.sleep(0.5)

            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except EOFError:
                break

        self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()


def main():
    """Run interactive tester."""
    print("🔬 MCP Interactive Tester")
    print("========================\n")

    tester = InteractiveTester()
    tester.start_server()
    tester.run_interactive()


if __name__ == "__main__":
    main()
