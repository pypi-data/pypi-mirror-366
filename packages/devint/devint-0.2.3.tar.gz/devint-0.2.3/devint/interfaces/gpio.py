import RPi.GPIO as GPIO
from typing import Optional, Dict, List, Union
from devices.base.interface import BaseInterface, InterfaceConfig


class GPIOInterface(BaseInterface):
    """GPIO interface implementation for Raspberry Pi"""

    def __init__(self, name: str, config: InterfaceConfig):
        super().__init__(name, config)
        self.mode = None
        self.pins = {}  # pin_number: {'mode': 'input'/'output', 'pull': None/'up'/'down'}

    def connect(self) -> bool:
        """Initialize GPIO"""
        try:
            # Set GPIO mode
            mode_str = self.config.parameters.get('mode', 'BCM')
            self.mode = GPIO.BCM if mode_str == 'BCM' else GPIO.BOARD
            GPIO.setmode(self.mode)
            GPIO.setwarnings(False)

            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to initialize GPIO: {e}")
            return False

    def disconnect(self) -> bool:
        """Cleanup GPIO"""
        try:
            GPIO.cleanup()
            self.pins.clear()
            self.is_connected = False
            return True
        except:
            return False

    def setup_pin(self, pin: int, mode: str = 'output',
                  initial: Optional[int] = None, pull: Optional[str] = None) -> bool:
        """Setup GPIO pin

        Args:
            pin: GPIO pin number
            mode: 'input' or 'output'
            initial: Initial value for output pins (0 or 1)
            pull: Pull resistor for input pins ('up', 'down', or None)
        """
        if not self.is_connected:
            return False

        try:
            if mode == 'output':
                GPIO.setup(pin, GPIO.OUT, initial=initial if initial is not None else GPIO.LOW)
            else:
                pull_mode = GPIO.PUD_OFF
                if pull == 'up':
                    pull_mode = GPIO.PUD_UP
                elif pull == 'down':
                    pull_mode = GPIO.PUD_DOWN
                GPIO.setup(pin, GPIO.IN, pull_up_down=pull_mode)

            self.pins[pin] = {'mode': mode, 'pull': pull}
            return True
        except Exception as e:
            print(f"GPIO setup error: {e}")
            return False

    def read(self, pin: int, count: int = 1, **kwargs) -> Optional[Union[int, List[int]]]:
        """Read GPIO pin(s)

        Args:
            pin: GPIO pin number or starting pin for multiple reads
            count: Number of consecutive pins to read
        """
        if not self.is_connected:
            return None

        try:
            with self._lock:
                if count == 1:
                    # Ensure pin is setup as input
                    if pin not in self.pins or self.pins[pin]['mode'] != 'input':
                        self.setup_pin(pin, 'input')
                    return GPIO.input(pin)
                else:
                    # Read multiple pins
                    values = []
                    for i in range(count):
                        p = pin + i
                        if p not in self.pins or self.pins[p]['mode'] != 'input':
                            self.setup_pin(p, 'input')
                        values.append(GPIO.input(p))
                    return values
        except Exception as e:
            print(f"GPIO read error: {e}")
            return None

    def write(self, pin: int, value: Union[int, bool, List[int]], **kwargs) -> bool:
        """Write to GPIO pin(s)

        Args:
            pin: GPIO pin number or starting pin for multiple writes
            value: Single value or list of values (0/1, True/False)
        """
        if not self.is_connected:
            return False

        try:
            with self._lock:
                if isinstance(value, (int, bool)):
                    # Single pin write
                    if pin not in self.pins or self.pins[pin]['mode'] != 'output':
                        self.setup_pin(pin, 'output')
                    GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)
                else:
                    # Multiple pin write
                    for i, val in enumerate(value):
                        p = pin + i
                        if p not in self.pins or self.pins[p]['mode'] != 'output':
                            self.setup_pin(p, 'output')
                        GPIO.output(p, GPIO.HIGH if val else GPIO.LOW)
                return True
        except Exception as e:
            print(f"GPIO write error: {e}")
            return False

    def add_event_detect(self, pin: int, edge: str, callback=None, bouncetime: int = 200):
        """Add edge detection for input pin

        Args:
            pin: GPIO pin number
            edge: 'rising', 'falling', or 'both'
            callback: Callback function(channel)
            bouncetime: Debounce time in ms
        """
        if not self.is_connected:
            return False

        try:
            edge_map = {
                'rising': GPIO.RISING,
                'falling': GPIO.FALLING,
                'both': GPIO.BOTH
            }

            if pin not in self.pins or self.pins[pin]['mode'] != 'input':
                self.setup_pin(pin, 'input')

            GPIO.add_event_detect(pin, edge_map.get(edge, GPIO.BOTH),
                                  callback=callback, bouncetime=bouncetime)
            return True
        except Exception as e:
            print(f"GPIO event detect error: {e}")
            return False