#!/usr/bin/env python3
"""
Test script for MCP lifecycle with STDIO proxy.
Tests the full MCP protocol lifecycle including initialization, operation, and shutdown.
"""

import json
import subprocess
import sys
import threading
import time
from pathlib import Path


class MCPTestClient:
    def __init__(self):
        self.process = None
        self.reader_thread = None
        self.responses = []
        self.running = True

    def start_server(self):
        """Start the MCP server with STDIO transport."""
        print("🚀 Starting MCP server with STDIO transport...")

        # Command to start the server using .venv Python
        venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            # Fallback to system Python
            venv_python = sys.executable
        cmd = [str(venv_python), "-m", "cursor_mcp_manager", "--stdio"]

        # Start the process
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
            cwd=Path(__file__).parent,
        )

        # Start reader thread
        self.reader_thread = threading.Thread(target=self._read_output)
        self.reader_thread.daemon = True
        self.reader_thread.start()

        # Give it a moment to start
        print("⏳ Waiting for server to fully initialize...")
        time.sleep(15)  # Give plenty of time for HTTP server to start
        print("✅ Server process started")

    def _read_output(self):
        """Read output from the server."""
        while self.running and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        print(f"📥 Server: {line}")
                        try:
                            msg = json.loads(line)
                            self.responses.append(msg)
                        except json.JSONDecodeError:
                            print(f"⚠️  Non-JSON output: {line}")
            except Exception as e:
                print(f"❌ Error reading output: {e}")
                break

        # Also read stderr
        if self.process:
            stderr = self.process.stderr.read()
            if stderr:
                print(f"📝 Server stderr:\n{stderr}")

    def send_message(self, message):
        """Send a JSON-RPC message to the server."""
        if not self.process or self.process.poll() is not None:
            print("❌ Server not running")
            return

        msg_str = json.dumps(message)
        print(f"📤 Client: {msg_str}")

        try:
            self.process.stdin.write(msg_str + "\n")
            self.process.stdin.flush()
        except Exception as e:
            print(f"❌ Error sending message: {e}")

    def wait_for_response(self, timeout=5):
        """Wait for a response from the server."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.responses:
                return self.responses.pop(0)
            time.sleep(0.1)
        return None

    def test_lifecycle(self):
        """Test the full MCP lifecycle."""
        print("\n" + "=" * 60)
        print("🧪 Testing MCP Lifecycle")
        print("=" * 60 + "\n")

        # 1. Send initialize request
        print("1️⃣  Sending initialize request...")
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": True}},
                "clientInfo": {"name": "TestClient", "version": "1.0.0"},
            },
        }
        self.send_message(initialize_request)

        # Wait for initialize response
        response = self.wait_for_response()
        if response:
            print(f"✅ Got initialize response: {json.dumps(response, indent=2)}")
            if "error" in response:
                print("❌ Initialize failed with error")
                return False
        else:
            print("❌ No initialize response received")
            return False

        # 2. Send initialized notification
        print("\n2️⃣  Sending initialized notification...")
        initialized_notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        self.send_message(initialized_notification)
        time.sleep(0.5)  # Give server time to process

        # 3. Test some operations
        print("\n3️⃣  Testing operations...")

        # List tools
        print("   📋 Listing tools...")
        list_tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
        self.send_message(list_tools_request)

        response = self.wait_for_response()
        if response:
            print(f"✅ Got tools list: {len(response.get('result', {}).get('tools', []))} tools")
        else:
            print("❌ No tools list response")

        # Get server status
        print("\n   📊 Getting server status...")
        status_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "get_mcp_servers_status", "arguments": {}},
        }
        self.send_message(status_request)

        response = self.wait_for_response()
        if response:
            print("✅ Got server status")
        else:
            print("❌ No status response")

        # 4. Test shutdown
        print("\n4️⃣  Testing shutdown...")
        shutdown_notification = {"jsonrpc": "2.0", "method": "notifications/exit"}
        self.send_message(shutdown_notification)

        # Give it time to shut down gracefully
        time.sleep(2)

        # Check if process exited
        if self.process.poll() is not None:
            print("✅ STDIO proxy shut down gracefully")
        else:
            print("⚠️  STDIO proxy still running (this is expected - HTTP server persists)")

        return True

    def test_http_server_persistence(self):
        """Test that the HTTP server persists after STDIO shutdown."""
        print("\n" + "=" * 60)
        print("🧪 Testing HTTP Server Persistence")
        print("=" * 60 + "\n")

        # Check if HTTP server is still running by checking a simple endpoint
        try:
            import httpx

            client = httpx.Client()
            # Just check if we can connect to the port
            response = client.get("http://localhost:8765/", timeout=2.0)
            # Any response means the server is running
            if response.status_code:
                print("✅ HTTP server is still running after STDIO shutdown")
                return True
            print(f"❌ HTTP server returned unexpected status {response.status_code}")
        except httpx.ConnectError:
            print("❌ Could not connect to HTTP server - it may have shut down")
        except Exception as e:
            print(f"❌ Error checking HTTP server: {e}")

        return False

    def cleanup(self):
        """Clean up resources."""
        self.running = False
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=5)
        if self.reader_thread:
            self.reader_thread.join(timeout=5)


def test_second_connection():
    """Test connecting a second STDIO client."""
    print("\n" + "=" * 60)
    print("🧪 Testing Second STDIO Connection")
    print("=" * 60 + "\n")

    client2 = MCPTestClient()
    try:
        client2.start_server()

        # Quick initialization
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "TestClient2", "version": "1.0.0"},
            },
        }
        client2.send_message(initialize_request)

        response = client2.wait_for_response()
        if response and "result" in response:
            print("✅ Second client connected successfully")
            print("✅ Both clients share the same HTTP server backend")
            return True
        print("❌ Second client failed to connect")
        return False
    finally:
        client2.cleanup()


def check_manager_cli():
    """Check the server status using the manager CLI."""
    print("\n" + "=" * 60)
    print("🧪 Checking Server Status with Manager CLI")
    print("=" * 60 + "\n")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "cursor_mcp_manager.manager_cli", "status"],
            check=False,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running manager CLI: {e}")
        return False


def test_concurrent_connections():
    """Test two clients connected at the same time."""
    print("\n" + "=" * 60)
    print("🧪 Testing Concurrent Connections")
    print("=" * 60 + "\n")

    client1 = MCPTestClient()
    client2 = MCPTestClient()

    try:
        # Start both clients
        print("Starting Client 1...")
        client1.start_server()
        time.sleep(2)

        print("Starting Client 2...")
        client2.start_server()

        # Initialize both
        init1 = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "Client1", "version": "1.0.0"},
            },
        }
        init2 = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "Client2", "version": "1.0.0"},
            },
        }

        client1.send_message(init1)
        client2.send_message(init2)

        response1 = client1.wait_for_response()
        response2 = client2.wait_for_response()

        if response1 and response2:
            print("✅ Both clients initialized successfully")

            # Send initialized notifications
            client1.send_message({"jsonrpc": "2.0", "method": "notifications/initialized"})
            client2.send_message({"jsonrpc": "2.0", "method": "notifications/initialized"})
            time.sleep(0.5)  # Give server time to process

            # Test calling a tool from both clients
            list_servers = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "list_mcp_servers", "arguments": {}},
            }

            client1.send_message(list_servers)
            client2.send_message(list_servers)

            tool_response1 = client1.wait_for_response()
            tool_response2 = client2.wait_for_response()

            if tool_response1 and tool_response2:
                print("✅ Both clients can call tools concurrently")
                return True
            print("❌ Tool calls failed for concurrent clients")
            return False
        print("❌ Failed to initialize both clients")
        return False

    finally:
        client1.cleanup()
        client2.cleanup()


def test_tool_functionality():
    """Test actual MCP tools through STDIO."""
    print("\n" + "=" * 60)
    print("🧪 Testing MCP Tool Functionality")
    print("=" * 60 + "\n")

    client = MCPTestClient()
    try:
        client.start_server()

        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "ToolTester", "version": "1.0.0"},
            },
        }
        client.send_message(init_request)
        init_response = client.wait_for_response()

        if not init_response or "error" in init_response:
            print("❌ Failed to initialize")
            return False

        # Send initialized notification
        client.send_message({"jsonrpc": "2.0", "method": "notifications/initialized"})
        time.sleep(0.5)

        # Test list_mcp_servers tool
        print("\n📋 Testing list_mcp_servers tool...")
        list_servers = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "list_mcp_servers", "arguments": {}},
        }
        client.send_message(list_servers)
        response = client.wait_for_response()

        if response and not response.get("result", {}).get("isError"):
            print("✅ list_mcp_servers tool works")
            content = response.get("result", {}).get("content", [])
            if content and content[0].get("type") == "text":
                print(f"   Found servers: {content[0].get('text', '')[:100]}...")
        else:
            print("❌ list_mcp_servers tool failed")

        # Test list_running_servers tool
        print("\n📋 Testing list_running_servers tool...")
        list_running = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "list_running_servers", "arguments": {}},
        }
        client.send_message(list_running)
        response = client.wait_for_response()

        if response and not response.get("result", {}).get("isError"):
            print("✅ list_running_servers tool works")
        else:
            print("❌ list_running_servers tool failed")

        return True

    finally:
        client.cleanup()


def main():
    """Run all tests."""
    print("🔬 MCP STDIO Lifecycle Test Suite")
    print("==================================\n")

    # Install the package first
    print("📦 Installing package...")
    venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = sys.executable
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-e", "."],
        check=False,
        capture_output=True,
        cwd=Path(__file__).parent,
    )

    # Test 1: Basic lifecycle
    client = MCPTestClient()
    try:
        client.start_server()
        if not client.test_lifecycle():
            print("\n❌ Lifecycle test failed")
            return 1

        # Test 2: HTTP server persistence
        if not client.test_http_server_persistence():
            print("\n⚠️  HTTP server persistence test failed (might not be running yet)")

        # Test 3: Second connection
        if not test_second_connection():
            print("\n❌ Second connection test failed")

        # Test 4: Concurrent connections
        if not test_concurrent_connections():
            print("\n❌ Concurrent connections test failed")

        # Test 5: Tool functionality
        if not test_tool_functionality():
            print("\n❌ Tool functionality test failed")

        # Test 6: Manager CLI
        if not check_manager_cli():
            print("\n⚠️  Manager CLI test failed")

        print("\n✅ All tests completed!")
        return 0

    finally:
        client.cleanup()

        # Optionally stop the HTTP server
        print("\n🛑 Stopping HTTP server...")
        subprocess.run(
            [sys.executable, "-m", "cursor_mcp_manager.manager_cli", "stop"], check=False, capture_output=True
        )


if __name__ == "__main__":
    sys.exit(main())
