from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import threading
import time
from flask import Flask, jsonify, request
import logging


class DeviceService(ABC):
    """Base class for device services"""

    def __init__(self, name: str, port: int = 5000):
        self.name = name
        self.port = port
        self.devices: Dict[str, 'BaseDevice'] = {}
        self.app = None
        self.running = False
        self._thread = None
        self.logger = logging.getLogger(f"DeviceService.{name}")

    @abstractmethod
    def setup_routes(self):
        """Setup Flask routes for the service"""
        pass

    def add_device(self, device: 'BaseDevice') -> bool:
        """Add device to service"""
        if device.device_id in self.devices:
            return False

        if device.initialize():
            self.devices[device.device_id] = device
            self.logger.info(f"Added device: {device.device_id}")
            return True
        return False

    def remove_device(self, device_id: str) -> bool:
        """Remove device from service"""
        if device_id in self.devices:
            device = self.devices[device_id]
            # Disconnect all interfaces
            for interface in device.interfaces.values():
                interface.disconnect()
            del self.devices[device_id]
            self.logger.info(f"Removed device: {device_id}")
            return True
        return False

    def create_app(self) -> Flask:
        """Create Flask application"""
        app = Flask(self.name)

        # Basic routes
        @app.route('/health')
        def health():
            return jsonify({
                'service': self.name,
                'status': 'running',
                'devices': len(self.devices)
            })

        @app.route('/devices')
        def list_devices():
            return jsonify({
                'devices': [
                    device.to_dict() for device in self.devices.values()
                ]
            })

        @app.route('/devices/<device_id>')
        def get_device(device_id):
            device = self.devices.get(device_id)
            if device:
                return jsonify(device.to_dict())
            return jsonify({'error': 'Device not found'}), 404

        @app.route('/devices/<device_id>/registers/<register_name>', methods=['GET'])
        def read_register(device_id, register_name):
            device = self.devices.get(device_id)
            if not device:
                return jsonify({'error': 'Device not found'}), 404

            value = device.read_register(register_name)
            return jsonify({
                'device_id': device_id,
                'register': register_name,
                'value': value
            })

        @app.route('/devices/<device_id>/registers/<register_name>', methods=['PUT'])
        def write_register(device_id, register_name):
            device = self.devices.get(device_id)
            if not device:
                return jsonify({'error': 'Device not found'}), 404

            data = request.get_json()
            value = data.get('value')

            success = device.write_register(register_name, value)
            return jsonify({
                'success': success,
                'device_id': device_id,
                'register': register_name,
                'value': value
            })

        # Add custom routes
        self.app = app
        self.setup_routes()

        return app

    def start(self, host: str = '0.0.0.0', debug: bool = False):
        """Start the service"""
        if self.running:
            return

        self.running = True
        app = self.create_app()

        # Run in thread
        self._thread = threading.Thread(
            target=lambda: app.run(host=host, port=self.port, debug=debug, use_reloader=False),
            daemon=True
        )
        self._thread.start()
        self.logger.info(f"Service started on {host}:{self.port}")

    def stop(self):
        """Stop the service"""
        self.running = False
        # Note: Stopping Flask gracefully is complex, might need additional implementation
        self.logger.info("Service stopped")