import spidev
from typing import Optional, List, Union
from devices.base.interface import BaseInterface, InterfaceConfig


class SPIInterface(BaseInterface):
    """SPI interface implementation for Raspberry Pi"""

    def __init__(self, name: str, config: InterfaceConfig):
        super().__init__(name, config)
        self.spi = None
        self.bus = 0
        self.device = 0

    def connect(self) -> bool:
        """Connect to SPI device"""
        try:
            # Parse port like /dev/spidev0.0
            if 'spidev' in self.config.port:
                parts = self.config.port.split('spidev')[-1].split('.')
                self.bus = int(parts[0])
                self.device = int(parts[1])
            else:
                self.bus = self.config.parameters.get('bus', 0)
                self.device = self.config.parameters.get('device', 0)

            self.spi = spidev.SpiDev()
            self.spi.open(self.bus, self.device)

            # Configure SPI parameters
            self.spi.max_speed_hz = self.config.parameters.get('speed_hz', 1000000)
            self.spi.mode = self.config.parameters.get('mode', 0)
            self.spi.bits_per_word = self.config.parameters.get('bits_per_word', 8)

            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to SPI device: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect from SPI device"""
        if self.spi:
            try:
                self.spi.close()
                self.spi = None
                self.is_connected = False
                return True
            except:
                pass
        return False

    def read(self, address: int = 0, count: int = 1, **kwargs) -> Optional[List[int]]:
        """Read from SPI device"""
        if not self.is_connected or not self.spi:
            return None

        try:
            with self._lock:
                # For SPI, we typically write address/command and read response
                command = kwargs.get('command', [address])
                if isinstance(command, int):
                    command = [command]

                # Pad command to match read length
                tx_data = command + [0] * (count - len(command))
                rx_data = self.spi.xfer2(tx_data)

                # Return only the read portion
                return rx_data[len(command):]
        except Exception as e:
            print(f"SPI read error: {e}")
            return None

    def write(self, address: int, data: Union[int, List[int]], **kwargs) -> bool:
        """Write to SPI device"""
        if not self.is_connected or not self.spi:
            return False

        try:
            with self._lock:
                if isinstance(data, int):
                    data = [data]

                # Prepend address/command if provided
                if address != 0:
                    tx_data = [address] + data
                else:
                    tx_data = data

                self.spi.xfer2(tx_data)
                return True
        except Exception as e:
            print(f"SPI write error: {e}")
            return False