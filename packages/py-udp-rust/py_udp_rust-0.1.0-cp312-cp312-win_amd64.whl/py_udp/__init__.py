"""
Python UDP library with Rust backend.

This module provides high-performance UDP server and client implementations
using Rust for the core networking functionality.
"""

from typing import Callable, Optional, Tuple, Union
import asyncio
import threading
import time

try:
    from ._py_udp import PyUdpServer, PyUdpClient, create_udp_server, create_udp_client
except ImportError:
    raise ImportError(
        "Failed to import Rust UDP module. Make sure the project is built with 'maturin develop'"
    )

__version__ = "0.1.0"
__all__ = ["UdpServer", "UdpClient", "MessageHandler"]


class MessageHandler:
    """Base class for UDP message handlers."""
    
    def __call__(self, data: bytes, source_address: str) -> None:
        """Handle incoming UDP message.
        
        Args:
            data: Received data as bytes
            source_address: Source address as string (host:port)
        """
        raise NotImplementedError("Subclasses must implement __call__")


class UdpServer:
    """High-performance UDP server with Rust backend."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 0):
        """Initialize UDP server.
        
        Args:
            host: Host address to bind to
            port: Port to bind to (0 for random port)
        """
        self._server = create_udp_server()
        self._host = host
        self._port = port
        self._bound = False
        self._message_handler: Optional[MessageHandler] = None

    def bind(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """Bind server to address.
        
        Args:
            host: Host address (optional, uses instance default)
            port: Port (optional, uses instance default)
        """
        if host is not None:
            self._host = host
        if port is not None:
            self._port = port
            
        addr = f"{self._host}:{self._port}"
        self._server.bind(addr)
        self._bound = True

    def set_message_handler(self, handler: Union[MessageHandler, Callable[[bytes, str], None]]) -> None:
        """Set message handler for incoming messages.
        
        Args:
            handler: Message handler function or object
        """
        if isinstance(handler, MessageHandler):
            self._message_handler = handler
            # Wrap the handler to call the __call__ method
            def wrapped_handler(data, source_address):
                handler(data, source_address)
            self._server.set_message_handler(wrapped_handler)
        else:
            self._message_handler = handler
            self._server.set_message_handler(handler)

    def start(self) -> None:
        """Start the server."""
        if not self._bound:
            raise RuntimeError("Server must be bound before starting")
        self._server.start()

    def stop(self) -> None:
        """Stop the server."""
        self._server.stop()

    def is_running(self) -> bool:
        """Check if server is running."""
        return self._server.is_running()

    def send_to(self, data: bytes, address: str) -> int:
        """Send data to specified address.
        
        Args:
            data: Data to send
            address: Destination address (host:port)
            
        Returns:
            Number of bytes sent
        """
        return self._server.send_to(data, address)

    @property
    def address(self) -> Tuple[str, int]:
        """Get server address."""
        if not self._bound:
            raise RuntimeError("Server not bound")
        return (self._host, self._port)


class UdpClient:
    """High-performance UDP client with Rust backend."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 0):
        """Initialize UDP client.
        
        Args:
            host: Host address to bind to
            port: Port to bind to (0 for random port)
        """
        self._client = create_udp_client()
        self._host = host
        self._port = port
        self._bound = False

    def bind(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """Bind client to address.
        
        Args:
            host: Host address (optional, uses instance default)
            port: Port (optional, uses instance default)
        """
        if host is not None:
            self._host = host
        if port is not None:
            self._port = port
            
        addr = f"{self._host}:{self._port}"
        self._client.bind(addr)
        self._bound = True

    def send_to(self, data: bytes, host: str, port: int) -> int:
        """Send data to specified address.
        
        Args:
            data: Data to send
            host: Destination host
            port: Destination port
            
        Returns:
            Number of bytes sent
        """
        if not self._bound:
            raise RuntimeError("Client must be bound before sending")
        addr = f"{host}:{port}"
        return self._client.send_to(data, addr)

    def recv_from(self) -> Tuple[bytes, str]:
        """Receive data from any address.
        
        Returns:
            Tuple of (data, source_address)
        """
        if not self._bound:
            raise RuntimeError("Client must be bound before receiving")
        return self._client.recv_from()

    @property
    def address(self) -> Tuple[str, int]:
        """Get client address."""
        if not self._bound:
            raise RuntimeError("Client not bound")
        return (self._host, self._port)


# Convenience functions
def create_server(host: str = "0.0.0.0", port: int = 0) -> UdpServer:
    """Create UDP server.
    
    Args:
        host: Host address
        port: Port number
        
    Returns:
        UdpServer instance
    """
    return UdpServer(host, port)


def create_client(host: str = "0.0.0.0", port: int = 0) -> UdpClient:
    """Create UDP client.
    
    Args:
        host: Host address
        port: Port number
        
    Returns:
        UdpClient instance
    """
    return UdpClient(host, port) 