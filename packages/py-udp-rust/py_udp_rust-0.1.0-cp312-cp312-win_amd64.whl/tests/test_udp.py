#!/usr/bin/env python3
"""
Tests for UDP functionality.
"""

import pytest
import time
import threading
from py_udp import UdpServer, UdpClient, MessageHandler


class TestMessageHandler(MessageHandler):
    """Test message handler for testing."""
    
    def __init__(self):
        self.received_messages = []
        self.message_count = 0
    
    def __call__(self, data, source_address: str) -> None:
        """Handle test message."""
        # Convert data to bytes if it's a list
        if isinstance(data, list):
            data = bytes(data)
        self.message_count += 1
        self.received_messages.append((data, source_address))


class TestUdpServer:
    """Test UDP server functionality."""
    
    def test_server_creation(self):
        """Test server creation."""
        server = UdpServer(host="127.0.0.1", port=0)
        assert server._host == "127.0.0.1"
        assert server._port == 0
        assert not server._bound
    
    def test_server_bind(self):
        """Test server binding."""
        server = UdpServer(host="127.0.0.1", port=0)
        server.bind()
        assert server._bound
    
    def test_server_message_handler(self):
        """Test setting message handler."""
        server = UdpServer()
        handler = TestMessageHandler()
        server.set_message_handler(handler)
        assert server._message_handler == handler


class TestUdpClient:
    """Test UDP client functionality."""
    
    def test_client_creation(self):
        """Test client creation."""
        client = UdpClient(host="127.0.0.1", port=0)
        assert client._host == "127.0.0.1"
        assert client._port == 0
        assert not client._bound
    
    def test_client_bind(self):
        """Test client binding."""
        client = UdpClient(host="127.0.0.1", port=0)
        client.bind()
        assert client._bound


class TestUdpCommunication:
    """Test UDP communication between client and server."""
    
    def test_basic_communication(self):
        """Test basic client-server communication."""
        # Create server
        server = UdpServer(host="127.0.0.1", port=8889)
        server.bind()
        
        # Create message handler
        handler = TestMessageHandler()
        server.set_message_handler(handler)
        
        # Start server
        server.start()
        time.sleep(0.1)  # Give server time to start
        
        # Create client
        client = UdpClient()
        client.bind()
        
        # Send message
        test_message = b"Hello, UDP!"
        bytes_sent = client.send_to(test_message, "127.0.0.1", 8889)
        assert bytes_sent > 0
        
        # Wait for message to be received
        time.sleep(0.1)
        
        # Check if message was received
        assert handler.message_count == 1
        assert len(handler.received_messages) == 1
        assert handler.received_messages[0][0] == test_message
        
        # Stop server
        server.stop()
    
    def test_multiple_messages(self):
        """Test sending multiple messages."""
        # Create server
        server = UdpServer(host="127.0.0.1", port=8890)
        server.bind()
        
        # Create message handler
        handler = TestMessageHandler()
        server.set_message_handler(handler)
        
        # Start server
        server.start()
        time.sleep(0.1)
        
        # Create client
        client = UdpClient()
        client.bind()
        
        # Send multiple messages
        messages = [b"Message 1", b"Message 2", b"Message 3"]
        for message in messages:
            client.send_to(message, "127.0.0.1", 8890)
            time.sleep(0.05)
        
        # Wait for all messages to be received
        time.sleep(0.2)
        
        # Check if all messages were received
        assert handler.message_count == 3
        assert len(handler.received_messages) == 3
        
        for i, message in enumerate(messages):
            assert handler.received_messages[i][0] == message
        
        # Stop server
        server.stop()


def test_concurrent_communication():
    """Test concurrent communication with multiple clients."""
    # Create server
    server = UdpServer(host="127.0.0.1", port=8891)
    server.bind()
    
    # Create message handler
    handler = TestMessageHandler()
    server.set_message_handler(handler)
    
    # Start server
    server.start()
    time.sleep(0.1)
    
    # Create multiple clients
    clients = []
    for i in range(3):
        client = UdpClient()
        client.bind()
        clients.append(client)
    
    # Send messages from all clients
    for i, client in enumerate(clients):
        message = f"Message from client {i}".encode('utf-8')
        client.send_to(message, "127.0.0.1", 8891)
    
    # Wait for messages to be received
    time.sleep(0.2)
    
    # Check if all messages were received
    assert handler.message_count == 3
    
    # Stop server
    server.stop()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 