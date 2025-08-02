from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field
import threading


@dataclass
class InterfaceConfig:
    """Konfiguracja interfejsu"""
    port: str  # np. /dev/ttyACM0, /dev/i2c-1, /dev/spidev0.0
    protocol: str  # np. "modbus_rtu", "i2c", "spi"
    parameters: Dict[str, Any] = field(default_factory=dict)

    def copy_with(self, **kwargs) -> 'InterfaceConfig':
        """Create a copy with updated parameters"""
        new_params = self.parameters.copy()
        new_params.update(kwargs)
        return InterfaceConfig(
            port=self.port,
            protocol=self.protocol,
            parameters=new_params
        )


class BaseInterface(ABC):
    """Bazowa klasa interfejsu komunikacyjnego"""

    def __init__(self, name: str, config: InterfaceConfig):
        self.name = name
        self.config = config
        self.is_connected = False
        self._lock = threading.Lock()
        self._config_lock = threading.Lock()

    @abstractmethod
    def connect(self) -> bool:
        """Nawiąż połączenie"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Rozłącz"""
        pass

    @abstractmethod
    def read(self, address: Any, count: int = 1, **kwargs) -> Optional[Any]:
        """Odczytaj dane"""
        pass

    @abstractmethod
    def write(self, address: Any, data: Any, **kwargs) -> bool:
        """Zapisz dane"""
        pass

    def reconfigure(self, **kwargs) -> bool:
        """Dynamically reconfigure interface parameters"""
        with self._config_lock:
            old_config = self.config.copy_with()
            try:
                # Update configuration
                self.config = self.config.copy_with(**kwargs)

                # If connected, reconnect with new parameters
                if self.is_connected:
                    self.disconnect()
                    return self.connect()
                return True
            except Exception as e:
                # Restore old configuration on error
                self.config = old_config
                raise e

    def get_parameter(self, key: str) -> Any:
        """Get configuration parameter"""
        return self.config.parameters.get(key)

    def set_parameter(self, key: str, value: Any) -> bool:
        """Set configuration parameter (requires reconnect if connected)"""
        return self.reconfigure(**{key: value})

    def to_dict(self) -> Dict[str, Any]:
        """Serializacja do słownika"""
        return {
            'name': self.name,
            'port': self.config.port,
            'protocol': self.config.protocol,
            'parameters': self.config.parameters,
            'is_connected': self.is_connected
        }