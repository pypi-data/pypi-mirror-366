import unittest
from unittest.mock import Mock, patch, MagicMock
from devint.base.interface import InterfaceConfig
from devint.interfaces.serial import SerialInterface
from devint.interfaces.i2c import I2CInterface


class TestSerialInterface(unittest.TestCase):
    """Test serial interface with baudrate changes"""

    def setUp(self):
        self.config = InterfaceConfig(
            port='/dev/ttyUSB0',
            protocol='modbus_rtu',
            parameters={
                'baudrate': 9600,
                'timeout': 1.0,
                'parity': 'N',
                'stopbits': 1,
                'bytesize': 8
            }
        )
        self.interface = SerialInterface('test_serial', self.config)

    @patch('serial.Serial')
    def test_connect(self, mock_serial):
        """Test serial connection"""
        mock_serial.return_value.is_open = True

        result = self.interface.connect()

        self.assertTrue(result)
        self.assertTrue(self.interface.is_connected)
        mock_serial.assert_called_once_with(
            port='/dev/ttyUSB0',
            baudrate=9600,
            timeout=1.0,
            parity='N',
            stopbits=1,
            bytesize=8
        )

    @patch('serial.Serial')
    def test_baudrate_change(self, mock_serial):
        """Test dynamic baudrate change"""
        mock_instance = Mock()
        mock_serial.return_value = mock_instance
        mock_instance.is_open = True

        # Connect with initial baudrate
        self.interface.connect()
        self.assertEqual(self.interface.get_parameter('baudrate'), 9600)

        # Change baudrate
        result = self.interface.set_parameter('baudrate', 19200)

        self.assertTrue(result)
        self.assertEqual(self.interface.get_parameter('baudrate'), 19200)

        # Verify reconnection happened with new baudrate
        self.assertEqual(mock_serial.call_count, 2)  # Initial + reconnect
        _, kwargs = mock_serial.call_args
        self.assertEqual(kwargs['baudrate'], 19200)

    @patch('serial.Serial')
    def test_reconfigure_multiple_parameters(self, mock_serial):
        """Test reconfiguring multiple parameters at once"""
        mock_serial.return_value.is_open = True

        self.interface.connect()

        # Reconfigure multiple parameters
        result = self.interface.reconfigure(
            baudrate=38400,
            timeout=2.0,
            parity='E'
        )

        self.assertTrue(result)
        self.assertEqual(self.interface.get_parameter('baudrate'), 38400)
        self.assertEqual(self.interface.get_parameter('timeout'), 2.0)
        self.assertEqual(self.interface.get_parameter('parity'), 'E')


class TestI2CInterface(unittest.TestCase):
    """Test I2C interface"""

    def setUp(self):
        self.config = InterfaceConfig(
            port='/dev/i2c-1',
            protocol='i2c',
            parameters={'bus': 1}
        )
        self.interface = I2CInterface('test_i2c', self.config)

    @patch('smbus2.SMBus')
    def test_connect(self, mock_smbus):
        """Test I2C connection"""
        result = self.interface.connect()

        self.assertTrue(result)
        self.assertTrue(self.interface.is_connected)
        mock_smbus.assert_called_once_with(1)

    @patch('smbus2.SMBus')
    def test_scan(self, mock_smbus):
        """Test I2C device scanning"""
        mock_bus = Mock()
        mock_smbus.return_value = mock_bus

        # Mock some devices at addresses 0x20 and 0x40
        def read_byte_side_effect(addr):
            if addr in [0x20, 0x40]:
                return 0xFF
            else:
                raise IOError("No device")

        mock_bus.read_byte.side_effect = read_byte_side_effect

        self.interface.connect()
        devices = self.interface.scan()

        self.assertIn(0x20, devices)
        self.assertIn(0x40, devices)
        self.assertEqual(len(devices), 2)


if __name__ == '__main__':
    unittest.main()