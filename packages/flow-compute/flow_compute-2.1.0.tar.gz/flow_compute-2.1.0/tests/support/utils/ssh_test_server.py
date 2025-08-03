"""Test SSH server using paramiko for integration testing.

A minimal but proper SSH server that handles real SSH connections
for testing SSH functionality without external infrastructure.
"""

import socket
import threading

import paramiko


class TestSSHServer(paramiko.ServerInterface):
    """SSH server implementation for testing."""

    def __init__(self, username="test", password="test"):
        self.username = username
        self.password = password
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == self.username and password == self.password:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        # Accept any key for testing
        if username == self.username:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password,publickey"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_exec_request(self, channel, command):
        """Handle command execution requests."""
        command = command.decode('utf-8')

        # Simple command responses for testing
        if command == "echo test":
            channel.send(b"test\n")
        elif command == "hostname":
            channel.send(b"test-server\n")
        elif command.startswith("tail"):
            # Mock log output
            channel.send(b"[2024-01-01] Starting task\n")
            channel.send(b"[2024-01-01] Task running\n")
        else:
            channel.send(f"Command executed: {command}\n".encode())

        channel.send_exit_status(0)
        channel.shutdown_write()  # Signal EOF by shutting down write side
        channel.shutdown_read()   # Shutdown read side too
        self.event.set()
        return True


class SSHTestServer:
    """Manages a test SSH server instance."""

    def __init__(self, port=0, username="test", password="test"):
        self.port = port
        self.username = username
        self.password = password
        self.server_socket = None
        self.server_thread = None
        self._running = False
        self._host_key = None

    def start(self):
        """Start the SSH server."""
        # Generate host key
        self._host_key = paramiko.RSAKey.generate(2048)

        # Create socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("127.0.0.1", self.port))
        self.server_socket.listen(5)

        # Get actual port if auto-assigned
        self.port = self.server_socket.getsockname()[1]

        self._running = True
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def _run_server(self):
        """Run the server loop."""
        while self._running:
            try:
                client, addr = self.server_socket.accept()
            except OSError:
                break

            # Handle client in thread
            thread = threading.Thread(target=self._handle_client, args=(client,))
            thread.daemon = True
            thread.start()

    def _handle_client(self, client_socket):
        """Handle a client connection."""
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(self._host_key)

        server = TestSSHServer(self.username, self.password)
        try:
            transport.start_server(server=server)

            # Keep transport open to handle multiple channel requests
            while self._running:
                channel = transport.accept(1)
                if channel is None:
                    # Check if transport is still active
                    if not transport.is_active():
                        break
                    continue

                # Handle the channel in a separate thread to allow concurrent channels
                import threading
                channel_thread = threading.Thread(
                    target=self._handle_channel,
                    args=(channel, server)
                )
                channel_thread.daemon = True
                channel_thread.start()

        except Exception:
            pass  # Client disconnected
        finally:
            transport.close()

    def _handle_channel(self, channel, server):
        """Handle a single channel."""
        try:
            # Wait for command execution with timeout
            if server.event.wait(10):
                server.event.clear()  # Reset for next command
            else:
                # Timeout - close the channel
                channel.send_exit_status(1)
                channel.shutdown_write()
                channel.shutdown_read()
        except Exception:
            pass  # Channel already closed
        finally:
            try:
                channel.close()
            except Exception:
                pass  # Already closed

    def stop(self):
        """Stop the SSH server."""
        self._running = False
        if self.server_socket:
            self.server_socket.close()
        if self.server_thread:
            self.server_thread.join(timeout=5)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def address(self):
        return ("127.0.0.1", self.port)


def create_test_client(server_address, username="test", password="test"):
    """Create an SSH client connected to test server."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=server_address[0],
        port=server_address[1],
        username=username,
        password=password,
        timeout=5
    )
    return client


# Example usage for tests:
if __name__ == "__main__":
    with SSHTestServer() as server:
        print(f"Test SSH server running on {server.address}")

        # Test connection
        client = create_test_client(server.address)
        stdin, stdout, stderr = client.exec_command("echo test")
        print(f"Response: {stdout.read().decode()}")
        client.close()
