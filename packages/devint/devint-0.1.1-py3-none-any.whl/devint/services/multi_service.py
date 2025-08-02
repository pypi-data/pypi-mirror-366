from typing import Dict, List, Optional
from devint.base.service import DeviceService
from devint.device_manager import DeviceManager
from flask import jsonify, request


class MultiDeviceService(DeviceService):
    """Service handling multiple devices"""

    def __init__(self, name: str = "MultiDevice", port: int = 5000):
        super().__init__(name, port)
        self.device_manager = DeviceManager()

    def setup_routes(self):
        """Setup additional routes for multi-device operations"""

        @self.app.route('/scan', methods=['POST'])
        def scan_devices():
            """Scan for devices on specified interfaces"""
            data = request.get_json()
            interface_type = data.get('interface', 'serial')

            # Perform scan based on interface type
            if interface_type == 'i2c':
                return self._scan_i2c_devices()
            elif interface_type == 'serial':
                return self._scan_serial_devices(data)
            elif interface_type == 'spi':
                return self._scan_spi_devices()

            return jsonify({'error': 'Unknown interface type'}), 400

        @self.app.route('/devices/batch', methods=['POST'])
        def batch_operation():
            """Perform batch operations on multiple devices"""
            data = request.get_json()
            operations = data.get('operations', [])
            results = []

            for op in operations:
                device_id = op.get('device_id')
                action = op.get('action')
                params = op.get('params', {})

                device = self.devices.get(device_id)
                if device:
                    if action == 'read':
                        value = device.read_register(params.get('register'))
                        results.append({
                            'device_id': device_id,
                            'action': action,
                            'result': value,
                            'success': value is not None
                        })
                    elif action == 'write':
                        success = device.write_register(
                            params.get('register'),
                            params.get('value')
                        )
                        results.append({
                            'device_id': device_id,
                            'action': action,
                            'success': success
                        })

            return jsonify({'results': results})

        @self.app.route('/devices/<device_id>/parameters', methods=['GET', 'PUT'])
        def device_parameters(device_id):
            """Get or update device interface parameters"""
            device = self.devices.get(device_id)
            if not device:
                return jsonify({'error': 'Device not found'}), 404

            if request.method == 'GET':
                # Get all interface parameters
                params = {}
                for name, interface in device.interfaces.items():
                    params[name] = interface.config.parameters
                return jsonify(params)
            else:  # PUT
                # Update interface parameters
                data = request.get_json()
                interface_name = data.get('interface', 'primary')
                parameters = data.get('parameters', {})

                interface = device.interfaces.get(interface_name)
                if interface:
                    success = interface.reconfigure(**parameters)
                    return jsonify({
                        'success': success,
                        'interface': interface_name,
                        'parameters': interface.config.parameters
                    })

                return jsonify({'error': 'Interface not found'}), 404

    def _scan_i2c_devices(self):
        """Scan for I2C devices"""
        from devint.interfaces.i2c import I2CInterface
        from devint.base.interface import InterfaceConfig

        results = []
        for bus in [0, 1]:  # Scan common I2C buses
            try:
                config = InterfaceConfig(
                    port=f"/dev/i2c-{bus}",
                    protocol="i2c",
                    parameters={'bus': bus}
                )
                interface = I2CInterface(f"i2c_scan_{bus}", config)

                if interface.connect():
                    addresses = interface.scan()
                    for addr in addresses:
                        results.append({
                            'interface': 'i2c',
                            'bus': bus,
                            'address': f"0x{addr:02X}",
                            'address_dec': addr
                        })
                    interface.disconnect()
            except Exception as e:
                self.logger.error(f"Error scanning I2C bus {bus}: {e}")

        return jsonify({'devices': results})

    def _scan_serial_devices(self, data):
        """Scan for serial/Modbus devices"""
        from devint import auto_detect_modbus_port

        ports = data.get('ports', [])
        baudrates = data.get('baudrates', [9600, 19200, 38400, 115200])

        results = []
        for port in ports:
            for baudrate in baudrates:
                result = auto_detect_modbus_port([baudrate], debug=True)
                if result:
                    results.append({
                        'interface': 'serial',
                        'port': result['port'],
                        'baudrate': result['baudrate'],
                        'protocol': 'modbus_rtu'
                    })

        return jsonify({'devices': results})