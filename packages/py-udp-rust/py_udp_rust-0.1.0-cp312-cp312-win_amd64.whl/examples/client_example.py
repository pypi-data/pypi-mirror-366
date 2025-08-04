#!/usr/bin/env python3
"""
UDP Client Example

This example demonstrates how to create a UDP client that sends messages
to a server and receives responses.
"""

import time
import threading
from py_udp import UdpClient


def receive_messages(client: UdpClient):
    """Receive messages in a separate thread."""
    print("Starting message receiver...")
    
    while True:
        try:
            # Add a small delay to avoid busy waiting
            time.sleep(0.1)
            
            data, source = client.recv_from()
            # Convert data to bytes if it's a list
            if isinstance(data, list):
                data = bytes(data)
            message = data.decode('utf-8')
            print(f"Received from {source}: {message}")
        except Exception as e:
            # Don't break on timeout errors
            if "timeout" not in str(e).lower():
                print(f"Error receiving message: {e}")
                break


def main():
    """Run UDP client."""
    print("Starting UDP Client...")
    
    # Create client
    client = UdpClient(host="127.0.0.1", port=0)
    
    # Bind to random port
    client.bind()
    print(f"Client bound to {client.address}")
    
    # Start receiver thread
    receiver_thread = threading.Thread(
        target=receive_messages, 
        args=(client,), 
        daemon=True
    )
    receiver_thread.start()
    
    # Server address
    server_host = "127.0.0.1"
    server_port = 8888
    
    print(f"Connecting to server at {server_host}:{server_port}")
    print("Sending messages automatically...")
    
    try:
        message_count = 0
        while True:
            message_count += 1
            
            # Create test message
            message = f"Hello, UDP! #{message_count}"
            data = message.encode('utf-8')
            
            # Send message
            try:
                bytes_sent = client.send_to(data, server_host, server_port)
                print(f"Sent: {message} ({bytes_sent} bytes)")
            except Exception as e:
                print(f"Error sending message: {e}")
            
            # Wait before sending next message
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\nStopping client...")
    
    print("Client stopped.")


if __name__ == "__main__":
    main() 