# py-udp

High-performance UDP networking library for Python with Rust backend.

## Architecture

This project uses PyO3 to create a Python extension module from Rust code:

1. **Rust Implementation** - Core UDP functionality implemented in Rust using Tokio
2. **PyO3 Bindings** - Python bindings created with PyO3
3. **Python API** - User-friendly Python interface

### Why This Architecture?

- **Performance**: Core networking implemented in Rust for maximum performance
- **Safety**: Rust's memory safety and zero-cost abstractions
- **Integration**: Seamless Python integration through PyO3
- **Modern**: Uses Tokio for efficient async I/O

## Features

- **High Performance**: Core networking implemented in Rust for maximum performance
- **Easy to Use**: Simple Python API for UDP server and client operations
- **Async Support**: Built on Tokio runtime for efficient async I/O
- **Type Safe**: Full type hints and error handling
- **Cross Platform**: Works on Windows, macOS, and Linux
- **Message Handlers**: Flexible callback system for processing incoming messages
- **Thread Safety**: Safe concurrent access with proper synchronization

## Installation

### Prerequisites

- Python 3.12+
- Rust (latest stable version)
- Cargo (comes with Rust)
- uv (recommended package manager)

### Build and Install

1. Clone the repository:
```bash
git clone <repository-url>
cd py-udp
```

2. Build and install the package:
```bash
uv run maturin develop
```

### Alternative: Using the Build Script

```bash
uv run python build.py
```

This script will:
- Check prerequisites
- Install maturin
- Build the Rust extension
- Install the Python package
- Run tests

## Quick Start

### UDP Server

```python
from py_udp import UdpServer, MessageHandler

class MyHandler(MessageHandler):
    def __call__(self, data: bytes, source_address: str):
        print(f"Received from {source_address}: {data.decode()}")
        # Process the message...

# Create and start server
server = UdpServer(host="127.0.0.1", port=8888)
server.bind()
server.set_message_handler(MyHandler())
server.start()

# Keep server running
import time
while server.is_running():
    time.sleep(1)
```

### UDP Client

```python
from py_udp import UdpClient

# Create client
client = UdpClient()
client.bind()

# Send message
message = "Hello, UDP!".encode('utf-8')
bytes_sent = client.send_to(message, "127.0.0.1", 8888)
print(f"Sent {bytes_sent} bytes")

# Receive response
data, source = client.recv_from()
print(f"Received from {source}: {data.decode()}")
```

## Examples

### Echo Server

The echo server example demonstrates how to create a UDP server that responds to incoming messages:

```python
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
```

Run the echo server example:

```bash
uv run python examples/server_example.py
```

### Echo Client

The echo client example demonstrates how to create a UDP client that sends messages and receives responses:

```python
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
```

In another terminal, run the client:

```bash
uv run python examples/client_example.py
```

The client will automatically send messages every 2 seconds and display received responses.

## Development

### Project Structure

```
py-udp/
├── src/                   # Rust source code
│   └── lib.rs            # Main Rust implementation
├── py_udp/               # Python package
│   ├── __init__.py       # Python API
│   └── ...
├── examples/             # Usage examples
│   ├── server_example.py # Echo server example
│   └── client_example.py # Echo client example
├── tests/                # Python tests
├── Cargo.toml           # Rust project config
├── pyproject.toml       # Python package config
└── README.md
```

### Working with Rust Code

```bash
# Build Rust extension
uv run maturin develop

# Run Rust tests
cargo test

# Run with debug output
RUST_LOG=debug cargo test
```

### Working with Python Package

```bash
# Install in development mode
uv run maturin develop

# Run Python tests
uv run pytest tests/

# Format code
uv run black .
uv run isort .
```

### Running Tests

```bash
# Rust tests
cargo test

# Python tests
uv run pytest tests/
```

## API Reference

### UdpServer

#### Constructor
```python
UdpServer(host: str = "0.0.0.0", port: int = 0)
```

#### Methods
- `bind(host: Optional[str] = None, port: Optional[int] = None) -> None`
  - Bind the server to a specific address and port
- `set_message_handler(handler: Union[MessageHandler, Callable]) -> None`
  - Set the message handler for processing incoming messages
- `start() -> None`
  - Start the server and begin listening for messages
- `stop() -> None`
  - Stop the server and clean up resources
- `is_running() -> bool`
  - Check if the server is currently running
- `send_to(data: bytes, address: str) -> int`
  - Send data to a specific address (host:port format)

#### Properties
- `address: Tuple[str, int]` - Server address

### UdpClient

#### Constructor
```python
UdpClient(host: str = "0.0.0.0", port: int = 0)
```

#### Methods
- `bind(host: Optional[str] = None, port: Optional[int] = None) -> None`
  - Bind the client to a specific address and port
- `send_to(data: bytes, host: str, port: int) -> int`
  - Send data to a specific host and port
- `recv_from() -> Tuple[bytes, str]`
  - Receive data from any address

#### Properties
- `address: Tuple[str, int]` - Client address

### MessageHandler

Base class for handling incoming UDP messages:

```python
class MyHandler(MessageHandler):
    def __call__(self, data: bytes, source_address: str) -> None:
        # Handle the message
        # data: received data as bytes
        # source_address: source address as string (host:port)
        pass
```

## Performance

The Rust backend provides significant performance improvements over pure Python implementations:

- **Lower Latency**: Direct system calls without Python GIL overhead
- **Higher Throughput**: Efficient async I/O with Tokio
- **Memory Efficiency**: Zero-copy operations where possible
- **Concurrent Processing**: True parallelism for multiple connections
- **Channel-based Communication**: Non-blocking message passing between Rust and Python

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure the Rust extension is built with `uv run maturin develop`
2. **Permission Denied**: Check if the port is already in use or requires elevated privileges
3. **Build Errors**: Ensure you have the latest Rust toolchain installed
4. **Runtime Errors**: Make sure the server is started before calling `send_to()`

### Debug Mode

Enable debug logging for Rust:

```bash
export RUST_LOG=debug
cargo test
```

### Testing the Installation

Run a simple test to verify everything works:

```bash
uv run python -c "from py_udp import UdpServer, UdpClient; print('✅ Installation successful!')"
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for both Rust and Python
5. Run tests and linting
6. Submit a pull request

### Development Workflow

1. **Rust Changes**: Work in `src/` directory
2. **Python Changes**: Work in `py_udp/` directory
3. **Integration**: Test both components work together
4. **Documentation**: Update README and docstrings
5. **Examples**: Update examples in `examples/` directory

### Code Style

- **Rust**: Follow Rust formatting guidelines with `cargo fmt`
- **Python**: Use Black for formatting and isort for imports
- **Documentation**: Keep docstrings up to date
- **Tests**: Maintain good test coverage for both Rust and Python 