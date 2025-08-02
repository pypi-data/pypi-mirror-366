from abc import ABC
from typing import Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class RegisterType(Enum):
    """Typy rejestrów"""
    COIL = "coil"  # Modbus coil (bool)
    DISCRETE_INPUT = "discrete_input"  # Modbus discrete input (bool)
    HOLDING_REGISTER = "holding"  # Modbus holding register (16-bit)
    INPUT_REGISTER = "input"  # Modbus input register (16-bit)
    MEMORY = "memory"  # Generic memory location
    OBJECT = "object"  # CANopen object
    TOPIC = "topic"  # MQTT topic


@dataclass
class BaseRegister:
    """Bazowa klasa rejestru/obiektu"""

    name: str
    address: Any  # Może być int (Modbus), string (MQTT topic), tuple (CANopen)
    register_type: RegisterType
    data_type: str = "uint16"  # uint16, int16, bool, float32, string, etc.
    access: str = "rw"  # r, w, rw
    description: str = ""
    unit: Optional[str] = None
    scale: float = 1.0
    offset: float = 0.0

    # Funkcje konwersji
    encode_func: Optional[Callable] = None
    decode_func: Optional[Callable] = None

    def encode(self, value: Any) -> Any:
        """Koduj wartość przed zapisem"""
        if self.encode_func:
            return self.encode_func(value)
        return int((value - self.offset) / self.scale)

    def decode(self, raw_value: Any) -> Any:
        """Dekoduj wartość po odczycie"""
        if self.decode_func:
            return self.decode_func(raw_value)
        return (raw_value * self.scale) + self.offset