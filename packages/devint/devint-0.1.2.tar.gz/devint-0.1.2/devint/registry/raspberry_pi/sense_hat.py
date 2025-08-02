from typing import Dict, Optional, Tuple
from devint.base import BaseDevice, DeviceIdentity, DeviceCapability
from devint.base.register import BaseRegister, RegisterType
from devint.interfaces.i2c import I2CInterface
from devint.interfaces.spi import SPIInterface
from sense_hat import SenseHat as SenseHatLib


class RaspberrySenseHAT(BaseDevice):
    """Raspberry Pi Sense HAT - 8x8 LED matrix, sensors, joystick"""

    # I2C addresses for Sense HAT components
    LED_MATRIX_ADDR = 0x46
    HUMIDITY_ADDR = 0x5F
    PRESSURE_ADDR = 0x5C
    MAGNETOMETER_ADDR = 0x1C
    ACCELEROMETER_ADDR = 0x6A

    def __init__(self, device_id: str, i2c_bus: int = 1):
        super().__init__(
            device_id=device_id,
            name="Raspberry Pi Sense HAT"
        )

        # Device identity
        self.identity = DeviceIdentity(
            manufacturer="Raspberry Pi Foundation",
            model="Sense HAT",
            hardware_version="1.0"
        )

        # Use the official Sense HAT library internally
        self.sense = None

        # I2C interface configuration
        i2c_config = InterfaceConfig(
            port=f"/dev/i2c-{i2c_bus}",
            protocol="i2c",
            parameters={'bus': i2c_bus}
        )

        # Add I2C interface
        self.add_interface('i2c', I2CInterface('i2c', i2c_config))

        # Define registers for sensors
        self._define_sensor_registers()

        # Define capabilities
        self.capabilities = {
            'led_matrix': DeviceCapability(
                name="8x8 RGB LED Matrix",
                description="64 RGB LEDs in 8x8 grid",
                data_type="rgb_array",
                read_only=False
            ),
            'temperature': DeviceCapability(
                name="Temperature Sensor",
                description="Temperature from humidity sensor",
                data_type="float32",
                unit="°C",
                read_only=True,
                min_value=-40,
                max_value=120
            ),
            'humidity': DeviceCapability(
                name="Humidity Sensor",
                description="Relative humidity",
                data_type="float32",
                unit="%",
                read_only=True,
                min_value=0,
                max_value=100
            ),
            'pressure': DeviceCapability(
                name="Pressure Sensor",
                description="Atmospheric pressure",
                data_type="float32",
                unit="mbar",
                read_only=True,
                min_value=260,
                max_value=1260
            ),
            'orientation': DeviceCapability(
                name="IMU Orientation",
                description="Pitch, roll, yaw from accelerometer/gyroscope",
                data_type="vector3",
                unit="degrees",
                read_only=True
            ),
            'joystick': DeviceCapability(
                name="5-way Joystick",
                description="Up, down, left, right, middle",
                data_type="events",
                read_only=True
            )
        }

    def _define_sensor_registers(self):
        """Define registers for all sensors"""

        # Temperature register
        self.add_register(BaseRegister(
            name="temperature",
            address=self.HUMIDITY_ADDR,
            register_type=RegisterType.MEMORY,
            data_type="float32",
            access="r",
            description="Temperature in Celsius",
            unit="°C",
            decode_func=lambda x: self.sense.temperature if self.sense else 0.0
        ))

        # Humidity register
        self.add_register(BaseRegister(
            name="humidity",
            address=self.HUMIDITY_ADDR,
            register_type=RegisterType.MEMORY,
            data_type="float32",
            access="r",
            description="Relative humidity",
            unit="%",
            decode_func=lambda x: self.sense.humidity if self.sense else 0.0
        ))

        # Pressure register
        self.add_register(BaseRegister(
            name="pressure",
            address=self.PRESSURE_ADDR,
            register_type=RegisterType.MEMORY,
            data_type="float32",
            access="r",
            description="Atmospheric pressure",
            unit="mbar",
            decode_func=lambda x: self.sense.pressure if self.sense else 0.0
        ))

        # LED matrix register (special handling)
        self.add_register(BaseRegister(
            name="led_matrix",
            address=self.LED_MATRIX_ADDR,
            register_type=RegisterType.MEMORY,
            data_type="custom",
            access="rw",
            description="8x8 RGB LED matrix",
            encode_func=self._encode_led_matrix,
            decode_func=self._decode_led_matrix
        ))

    def initialize(self) -> bool:
        """Initialize Sense HAT"""
        try:
            # Initialize I2C interface
            if not self.interfaces['i2c'].connect():
                return False

            # Initialize Sense HAT library
            self.sense = SenseHatLib()
            self.sense.clear()

            self.is_online = True
            return True
        except Exception as e:
            print(f"Failed to initialize Sense HAT: {e}")
            return False

    def read_register(self, register_name: str) -> Optional[Any]:
        """Read register value"""
        if not self.sense:
            return None

        register = self.registers.get(register_name)
        if not register:
            return None

        try:
            # Use decode function if available
            if register.decode_func:
                return register.decode_func(None)

            # Direct sensor readings
            if register_name == "orientation":
                return self.sense.get_orientation()
            elif register_name == "accelerometer":
                return self.sense.get_accelerometer_raw()
            elif register_name == "compass":
                return self.sense.get_compass_raw()

            return None
        except Exception as e:
            print(f"Error reading {register_name}: {e}")
            return None

    def write_register(self, register_name: str, value: Any) -> bool:
        """Write register value"""
        if not self.sense:
            return False

        register = self.registers.get(register_name)
        if not register or register.access == 'r':
            return False

        try:
            if register_name == "led_matrix":
                # Handle LED matrix writes
                if isinstance(value, list) and len(value) == 64:
                    self.sense.set_pixels(value)
                    return True
                elif isinstance(value, str):
                    # Show message
                    self.sense.show_message(value)
                    return True

            return False
        except Exception as e:
            print(f"Error writing {register_name}: {e}")
            return False

    def _encode_led_matrix(self, pixels: list) -> bytes:
        """Encode LED matrix data for I2C transmission"""
        # Convert list of [R,G,B] to bytes
        data = []
        for pixel in pixels:
            if isinstance(pixel, (list, tuple)) and len(pixel) >= 3:
                data.extend([pixel[0] & 0xFF, pixel[1] & 0xFF, pixel[2] & 0xFF])
        return bytes(data)

    def _decode_led_matrix(self, data: bytes) -> list:
        """Decode LED matrix data from I2C"""
        if not self.sense:
            return [[0, 0, 0]] * 64
        return self.sense.get_pixels()

    # High-level methods
    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> bool:
        """Set single pixel color"""
        if self.sense and 0 <= x < 8 and 0 <= y < 8:
            self.sense.set_pixel(x, y, color)
            return True
        return False

    def clear_display(self, color: Tuple[int, int, int] = (0, 0, 0)) -> bool:
        """Clear LED matrix"""
        if self.sense:
            self.sense.clear(color)
            return True
        return False

    def show_message(self, text: str, scroll_speed: float = 0.1,
                     text_color: Tuple[int, int, int] = (255, 255, 255),
                     back_color: Tuple[int, int, int] = (0, 0, 0)) -> bool:
        """Show scrolling message"""
        if self.sense:
            self.sense.show_message(text, scroll_speed, text_color, back_color)
            return True
        return False

    def get_sensor_data(self) -> Dict[str, float]:
        """Get all sensor readings"""
        if not self.sense:
            return {}

        return {
            'temperature': self.sense.temperature,
            'humidity': self.sense.humidity,
            'pressure': self.sense.pressure,
            'temperature_from_pressure': self.sense.get_temperature_from_pressure(),
            'temperature_from_humidity': self.sense.get_temperature_from_humidity()
        }