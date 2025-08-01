# ModbusIM - Modbus Device Simulator

A Python package for simulating Modbus RTU/ASCII/TCP devices for testing and development purposes.

[![PyPI version](https://badge.fury.io/py/modbusim.svg)](https://badge.fury.io/py/modbusim)
[![Python Version](https://img.shields.io/badge/python-3.8.1+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0 ](https://img.shields.io/badge/License-Apache 2.0 -yellow.svg)](https://opensource.org/licenses/Apache 2.0 )

## Features

- Simulate Modbus RTU/ASCII/TCP devices
- Support for all standard Modbus function codes
- Easy-to-use CLI interface
- Programmatic API for integration with tests
- Configurable device behavior
- Docker support for easy deployment

## Installation

### Using pip

```bash
pip install modbusim
```

### Using Poetry (for development)

```bash
git clone https://github.com/yourusername/modbusim.git
cd modbusim
poetry install
```

### Using Docker

```bash
# Build the image
docker build -t modbusim .

# Run the Modbus TCP simulator
docker run -p 5020:5020 modbusim
```

Or using Docker Compose:

```bash
docker-compose up -d
```

## Usage

### Command Line Interface

Start a Modbus RTU simulator:

```bash
modbusim rtu --port /tmp/ptyp0 --baudrate 9600
```

Start a Modbus TCP simulator:

```bash
modbusim tcp --host 0.0.0.0 --port 5020
```

### Python API

```python
from modbusim import ModbusSimulator

# Create a simulator instance
simulator = ModbusSimulator(
    mode="rtu",  # or "tcp"
    port="/tmp/ptyp0",  # or host="0.0.0.0" for TCP
    baudrate=9600
)

# Start the simulator
simulator.start()

try:
    # Your test code here
    while True:
        # Keep the simulator running
        pass
except KeyboardInterrupt:
    # Stop the simulator
    simulator.stop()
```

## Development

### Running Tests

```bash
make test
```

### Linting and Formatting

```bash
make lint    # Run linters
make format  # Format code
```

### Building and Publishing

```bash
make build    # Build the package
make publish  # Publish to PyPI
```

## Docker Development

### Build the development image

```bash
docker-compose -f docker-compose.dev.yml build
```

### Run tests in Docker

```bash
docker-compose -f docker-compose.dev.yml run --rm modbusim make test
```

### Start a development shell

```bash
docker-compose -f docker-compose.dev.yml run --rm --service-ports modbusim bash
```

## License

Apache 2.0  - See [LICENSE](LICENSE) for more information.
