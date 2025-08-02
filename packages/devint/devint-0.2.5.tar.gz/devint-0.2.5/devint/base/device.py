from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DeviceIdentity:
    """Identyfikacja urządzenia"""
    manufacturer: str
    model: str
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None


@dataclass
class DeviceCapability:
    """Możliwości urządzenia"""
    name: str
    description: str
    read_only: bool = False
    data_type: str = "bool"
    unit: Optional[str] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None


class BaseDevice(ABC):
    """Bazowa klasa dla wszystkich urządzeń elektronicznych"""

    def __init__(self, device_id: str, name: str):
        self.device_id = device_id
        self.name = name
        self.identity = DeviceIdentity(
            manufacturer="Unknown",
            model="Unknown"
        )
        self.interfaces: Dict[str, 'BaseInterface'] = {}
        self.registers: Dict[str, 'BaseRegister'] = {}
        self.capabilities: Dict[str, DeviceCapability] = {}
        self.metadata: Dict[str, Any] = {}
        self.last_seen = datetime.now()
        self.is_online = False

    @abstractmethod
    def initialize(self) -> bool:
        """Inicjalizacja urządzenia"""
        pass

    @abstractmethod
    def read_register(self, register_name: str) -> Any:
        """Odczyt rejestru"""
        pass

    @abstractmethod
    def write_register(self, register_name: str, value: Any) -> bool:
        """Zapis do rejestru"""
        pass

    def add_interface(self, name: str, interface: 'BaseInterface'):
        """Dodaj interfejs komunikacyjny"""
        self.interfaces[name] = interface

    def add_register(self, register: 'BaseRegister'):
        """Dodaj rejestr"""
        self.registers[register.name] = register

    def to_dict(self) -> Dict[str, Any]:
        """Serializacja do słownika"""
        return {
            'device_id': self.device_id,
            'name': self.name,
            'identity': {
                'manufacturer': self.identity.manufacturer,
                'model': self.identity.model,
                'serial_number': self.identity.serial_number,
                'firmware_version': self.identity.firmware_version,
                'hardware_version': self.identity.hardware_version
            },
            'interfaces': {
                name: iface.to_dict()
                for name, iface in self.interfaces.items()
            },
            'capabilities': {
                name: {
                    'name': cap.name,
                    'description': cap.description,
                    'read_only': cap.read_only,
                    'data_type': cap.data_type,
                    'unit': cap.unit
                }
                for name, cap in self.capabilities.items()
            },
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat()
        }