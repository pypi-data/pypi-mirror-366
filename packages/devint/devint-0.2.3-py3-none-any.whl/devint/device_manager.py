import json
from typing import Dict, List, Optional, Type
from pathlib import Path
from devices.base import BaseDevice


class DeviceManager:
    """Manager do zarządzania urządzeniami"""

    def __init__(self, config_path: Optional[Path] = None):
        self.devices: Dict[str, BaseDevice] = {}
        self.config_path = config_path or Path("devices.json")
        self.device_registry: Dict[str, Type[BaseDevice]] = {}

    def register_device_type(self, type_name: str, device_class: Type[BaseDevice]):
        """Rejestruj typ urządzenia"""
        self.device_registry[type_name] = device_class

    def add_device(self, device: BaseDevice) -> bool:
        """Dodaj urządzenie"""
        if device.device_id in self.devices:
            return False
        self.devices[device.device_id] = device
        return True

    def get_device(self, device_id: str) -> Optional[BaseDevice]:
        """Pobierz urządzenie"""
        return self.devices.get(device_id)

    def discover_devices(self, interface_type: str = "serial") -> List[BaseDevice]:
        """Automatyczne wykrywanie urządzeń"""
        discovered = []
        # Implementacja skanowania portów i wykrywania urządzeń
        # Na podstawie istniejącego kodu auto_detect_modbus_port
        return discovered

    def save_configuration(self):
        """Zapisz konfigurację urządzeń"""
        config = {
            'devices': [
                {
                    'device_id': device.device_id,
                    'type': device.__class__.__name__,
                    'config': device.to_dict()
                }
                for device in self.devices.values()
            ]
        }

        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def load_configuration(self):
        """Wczytaj konfigurację urządzeń"""
        if not self.config_path.exists():
            return

        with open(self.config_path, 'r') as f:
            config = json.load(f)

        for device_config in config.get('devices', []):
            device_type = device_config.get('type')
            device_class = self.device_registry.get(device_type)

            if device_class:
                # Odtwórz urządzenie z konfiguracji
                # Wymaga dodatkowej implementacji w klasach urządzeń
                pass