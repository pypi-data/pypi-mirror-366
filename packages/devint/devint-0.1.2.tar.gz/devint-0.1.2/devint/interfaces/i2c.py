import smbus2
import time
from typing import Optional, List, Union
from devint.base.interface import BaseInterface, InterfaceConfig


class I2CInterface(BaseInterface):
    """I2C interface implementation for Raspberry Pi"""

    def __init__(self, name: str, config: InterfaceConfig):
        super().__init__(name, config)
        self.bus = None
        self.bus_number = None

    def connect(self) -> bool:
        """Connect to I2C bus"""
        try:
            # Extract bus number from port (e.g., /dev/i2c-1 -> 1)
            if 'i2c-' in self.config.port:
                self.bus_number = int(self.config.port.split('-')[-1])
            else:
                self.bus_number = self.config.parameters.get('bus', 1)

            self.bus = smbus2.SMBus(self.bus_number)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to I2C bus: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect from I2C bus"""
        if self.bus:
            try:
                self.bus.close()
                self.bus = None
                self.is_connected = False
                return True
            except:
                pass
        return False

    def read(self, address: int, register: Optional[int] = None,
             count: int = 1, **kwargs) -> Optional[Union[int, List[int]]]:
        """Read from I2C device

        Args:
            address: I2C device address (7-bit)
            register: Register address to read from (optional)
            count: Number of bytes to read

        Returns:
            Single byte or list of bytes
        """
        if not self.is_connected or not self.bus:
            return None

        try:
            with self._lock:
                if register is not None:
                    # Read from specific register
                    if count == 1:
                        return self.bus.read_byte_data(address, register)
                    else:
                        return self.bus.read_i2c_block_data(address, register, count)
                else:
                    # Read without register
                    if count == 1:
                        return self.bus.read_byte(address)
                    else:
                        return [self.bus.read_byte(address) for _ in range(count)]
        except Exception as e:
            print(f"I2C read error: {e}")
            return None

    def write(self, address: int, data: Union[int, List[int]],
              register: Optional[int] = None, **kwargs) -> bool:
        """Write to I2C device

        Args:
            address: I2C device address (7-bit)
            data: Byte or list of bytes to write
            register: Register address to write to (optional)

        Returns:
            Success status
        """
        if not self.is_connected or not self.bus:
            return False

        try:
            with self._lock:
                if isinstance(data, int):
                    if register is not None:
                        self.bus.write_byte_data(address, register, data)
                    else:
                        self.bus.write_byte(address, data)
                else:
                    if register is not None:
                        self.bus.write_i2c_block_data(address, register, data)
                    else:
                        for byte in data:
                            self.bus.write_byte(address, byte)
                return True
        except Exception as e:
            print(f"I2C write error: {e}")
            return False

    def scan(self) -> List[int]:
        """Scan I2C bus for devices

        Returns:
            List of detected I2C addresses
        """
        if not self.is_connected:
            return []

        devices = []
        for address in range(0x03, 0x78):  # Valid 7-bit I2C addresses
            try:
                self.bus.read_byte(address)
                devices.append(address)
            except:
                pass

        return devices