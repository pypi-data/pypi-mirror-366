#!/usr/bin/env python3
"""
UDP Server Example

This example demonstrates how to create a UDP server that echoes back
received messages with additional information.
"""

import time
from py_udp import UdpServer, MessageHandler


class EchoHandler(MessageHandler):
    """Echo handler that responds to incoming messages."""
    
    def __init__(self, server: UdpServer):
        self.server = server
        self.message_count = 0
    
    def __call__(self, data, source_address: str) -> None:
        """Handle incoming message and send response."""
        # Convert data to bytes if it's a list
        if isinstance(data, list):
            data = bytes(data)
            
        self.message_count += 1
        
        # Decode message
        try:
            message = data.decode('utf-8')
        except UnicodeDecodeError:
            message = f"<binary data: {len(data)} bytes>"
        
        print(f"[{self.message_count}] Received from {source_address}: {message}")
        
        # Create response
        response = f"Echo #{self.message_count}: {message}"
        response_data = response.encode('utf-8')
        
        # Send response using the server's send_to method
        try:
            bytes_sent = self.server.send_to(response_data, source_address)
            print(f"Sent {bytes_sent} bytes to {source_address}")
        except Exception as e:
            print(f"Error sending response: {e}")


def main():
    """Run UDP echo server."""
    print("Starting UDP Echo Server...")
    
    # Create server
    server = UdpServer(host="127.0.0.1", port=8888)
    
    # Bind to address
    server.bind()
    print(f"Server bound to {server.address}")
    
    # Set message handler
    handler = EchoHandler(server)
    server.set_message_handler(handler)
    
    # Start server
    server.start()
    print("Server started. Press Ctrl+C to stop.")
    
    try:
        # Keep server running
        while server.is_running():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()
        print("Server stopped.")


if __name__ == "__main__":
    main() 