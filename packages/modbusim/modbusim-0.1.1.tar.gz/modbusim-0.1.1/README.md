# ModbusIM - Modbus Device Simulator

A Python package for simulating Modbus RTU/ASCII/TCP devices for testing and development purposes.

## Features

- Simulate Modbus RTU/ASCII/TCP devices
- Support for all standard Modbus function codes
- Easy-to-use CLI interface
- Programmatic API for integration with tests
- Configurable device behavior

## Installation

```bash
pip install modbusim
```

For development:

```bash
git clone https://github.com/yourusername/modbusim.git
cd modbusim
poetry install
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
    mode="rtu",
    port="/tmp/ptyp0",
    baudrate=9600
)

# Start the simulator
simulator.start()

# Your test code here

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
make lint
make format
```

## License

MIT
