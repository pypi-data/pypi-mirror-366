# DevInt - Unified Device Interface

[![PyPI](https://img.shields.io/pypi/v/devint)](https://pypi.org/project/devint/)
[![Python Version](https://img.shields.io/pypi/pyversions/devint)](https://pypi.org/project/devint/)
[![License](https://img.shields.io/pypi/l/devint)](https://github.com/softreck/devint/blob/main/LICENSE)

A Python library for interacting with various hardware devices and protocols through a unified interface.

## Features

- **Unified API** for different hardware interfaces (I2C, SPI, GPIO, Serial, etc.)
- **Device Registry** for easy hardware component management
- **Web Interface** for remote monitoring and control
- **Multiple Protocol Support**:
  - Modbus RTU/TCP
  - I2C/SMBus
  - SPI
  - GPIO
  - 1-Wire
  - CAN bus
  - MQTT
- **Pre-built Device Support** for common hardware (Raspberry Pi HATs, Waveshare modules, etc.)

## Installation

```bash
pip install devint
```

For development:

```bash
git clone https://github.com/softreck/devint.git
cd devint
poetry install
```

## Quick Start

```python
from devint import MultiDeviceService
from devint.registry.raspberry_pi.sense_hat import RaspberrySenseHAT

# Create a service
service = MultiDeviceService()

# Add a device
sense_hat = RaspberrySenseHAT("sense_hat_1")
service.add_device(sense_hat)

# Start the service (includes web interface on port 5000)
service.start()
```

## Documentation

For full documentation, please visit [https://github.com/pyfunc/devint](https://github.com/softreck/devint)

## License

Apache 2.0 - See [LICENSE](LICENSE) for more information.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.
