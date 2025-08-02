# devices/registry/waveshare/io_8ch.py
from typing import List, Optional
from devices.base import BaseDevice, DeviceIdentity, DeviceCapability
from devices.base.register import BaseRegister, RegisterType
from devices.interfaces.serial import SerialInterface
from devices.protocols.modbus_rtu import ModbusRTUProtocol


class WaveshareIO8CH(BaseDevice):
    """Waveshare Modbus RTU IO 8CH Module"""

    def __init__(self, device_id: str, port: str, unit_id: int = 1, baudrate: int = 9600):
        super().__init__(
            device_id=device_id,
            name=f"Waveshare IO 8CH (Unit {unit_id})"
        )

        # Identyfikacja urządzenia
        self.identity = DeviceIdentity(
            manufacturer="Waveshare",
            model="Modbus RTU IO 8CH",
            firmware_version="1.0"
        )

        # Konfiguracja interfejsu
        interface_config = InterfaceConfig(
            port=port,
            protocol="modbus_rtu",
            parameters={
                'baudrate': baudrate,
                'unit_id': unit_id,
                'parity': 'N',
                'stopbits': 1,
                'bytesize': 8,
                'timeout': 1.0
            }
        )

        # Dodaj interfejs
        self.add_interface('primary', SerialInterface('primary', interface_config))

        # Zdefiniuj rejestry dla 8 wyjść
        for i in range(8):
            self.add_register(BaseRegister(
                name=f"output_{i}",
                address=i,
                register_type=RegisterType.COIL,
                data_type="bool",
                access="rw",
                description=f"Digital Output Channel {i}"
            ))

        # Zdefiniuj rejestry dla 8 wejść
        for i in range(8):
            self.add_register(BaseRegister(
                name=f"input_{i}",
                address=i,
                register_type=RegisterType.DISCRETE_INPUT,
                data_type="bool",
                access="r",
                description=f"Digital Input Channel {i}"
            ))

        # Rejestry konfiguracji
        for i in range(8):
            self.add_register(BaseRegister(
                name=f"output_mode_{i}",
                address=0x1000 + i,
                register_type=RegisterType.HOLDING_REGISTER,
                data_type="uint16",
                access="rw",
                description=f"Output Channel {i} Mode (0=Normal, 1=Linkage, 2=Toggle, 3=Edge)"
            ))

        # Możliwości urządzenia
        self.capabilities = {
            'digital_outputs': DeviceCapability(
                name="Digital Outputs",
                description="8 digital output channels",
                data_type="bool",
                read_only=False
            ),
            'digital_inputs': DeviceCapability(
                name="Digital Inputs",
                description="8 digital input channels",
                data_type="bool",
                read_only=True
            ),
            'output_modes': DeviceCapability(
                name="Output Modes",
                description="Configurable output modes",
                data_type="enum",
                read_only=False
            )
        }

    def initialize(self) -> bool:
        """Inicjalizacja urządzenia"""
        interface = self.interfaces.get('primary')
        if interface and interface.connect():
            self.is_online = True
            return True
        return False

    def read_register(self, register_name: str) -> Optional[Any]:
        """Odczyt rejestru"""
        register = self.registers.get(register_name)
        interface = self.interfaces.get('primary')

        if not register or not interface:
            return None

        raw_value = interface.read(register.address)
        if raw_value is not None:
            return register.decode(raw_value)
        return None

    def write_register(self, register_name: str, value: Any) -> bool:
        """Zapis do rejestru"""
        register = self.registers.get(register_name)
        interface = self.interfaces.get('primary')

        if not register or not interface or register.access == 'r':
            return False

        encoded_value = register.encode(value)
        return interface.write(register.address, encoded_value)

    # Metody wysokiego poziomu
    def set_output(self, channel: int, state: bool) -> bool:
        """Ustaw stan wyjścia"""
        return self.write_register(f"output_{channel}", state)

    def get_input(self, channel: int) -> Optional[bool]:
        """Odczytaj stan wejścia"""
        return self.read_register(f"input_{channel}")

    def get_all_outputs(self) -> List[bool]:
        """Odczytaj wszystkie wyjścia"""
        return [self.read_register(f"output_{i}") or False for i in range(8)]

    def get_all_inputs(self) -> List[bool]:
        """Odczytaj wszystkie wejścia"""
        return [self.read_register(f"input_{i}") or False for i in range(8)]