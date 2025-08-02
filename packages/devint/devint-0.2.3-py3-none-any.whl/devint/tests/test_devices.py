import unittest
from unittest.mock import Mock, patch
from devices.registry.waveshare.io_8ch import WaveshareIO8CH
from devices.registry.raspberry_pi.sense_hat import RaspberrySenseHAT


class TestWaveshareIO8CH(unittest.TestCase):
    """Test Waveshare IO 8CH device"""

    def setUp(self):
        self.device = WaveshareIO8CH(
            device_id='test_io8ch',
            port='/dev/ttyUSB0',
            unit_id=1,
            baudrate=9600
        )

    def test_device_properties(self):
        """Test device basic properties"""
        self.assertEqual(self.device.device_id, 'test_io8ch')
        self.assertEqual(self.device.name, 'Waveshare IO 8CH (Unit 1)')
        self.assertEqual(self.device.identity.manufacturer, 'Waveshare')
        self.assertEqual(self.device.identity.model, 'Modbus RTU IO 8CH')

    def test_registers_defined(self):
        """Test that all registers are properly defined"""
        # Check output registers
        for i in range(8):
            self.assertIn(f'output_{i}', self.device.registers)
            self.assertIn(f'input_{i}', self.device.registers)
            self.assertIn(f'output_mode_{i}', self.device.registers)

    @patch('devices.interfaces.serial.SerialInterface.connect')
    def test_initialize(self, mock_connect):
        """Test device initialization"""
        mock_connect.return_value = True

        result = self.device.initialize()

        self.assertTrue(result)
        self.assertTrue(self.device.is_online)
        mock_connect.assert_called_once()

    def test_set_output(self):
        """Test setting output channel"""
        self.device.interfaces['primary'] = Mock()
        self.device.interfaces['primary'].write.return_value = True

        result = self.device.set_output(0, True)

        self.assertTrue(result)
        self.device.interfaces['primary'].write.assert_called_once()


class TestRaspberrySenseHAT(unittest.TestCase):
    """Test Raspberry Pi Sense HAT"""

    def setUp(self):
        self.device = RaspberrySenseHAT(
            device_id='test_sense_hat',
            i2c_bus=1
        )

    def test_device_properties(self):
        """Test device basic properties"""
        self.assertEqual(self.device.device_id, 'test_sense_hat')
        self.assertEqual(self.device.name, 'Raspberry Pi Sense HAT')
        self.assertEqual(self.device.identity.manufacturer, 'Raspberry Pi Foundation')

    def test_capabilities(self):
        """Test device capabilities"""
        self.assertIn('led_matrix', self.device.capabilities)
        self.assertIn('temperature', self.device.capabilities)
        self.assertIn('humidity', self.device.capabilities)
        self.assertIn('pressure', self.device.capabilities)
        self.assertIn('orientation', self.device.capabilities)

    @patch('sense_hat.SenseHat')
    @patch('devices.interfaces.i2c.I2CInterface.connect')
    def test_initialize(self, mock_i2c_connect, mock_sense_hat):
        """Test Sense HAT initialization"""
        mock_i2c_connect.return_value = True
        mock_sense_instance = Mock()
        mock_sense_hat.return_value = mock_sense_instance

        result = self.device.initialize()

        self.assertTrue(result)
        self.assertTrue(self.device.is_online)
        mock_i2c_connect.assert_called_once()
        mock_sense_instance.clear.assert_called_once()


if __name__ == '__main__':
    unittest.main()