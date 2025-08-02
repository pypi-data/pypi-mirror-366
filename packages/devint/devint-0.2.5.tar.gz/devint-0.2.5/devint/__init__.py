"""
DevInt - Unified Device Interface

A Python library for interacting with various hardware devices and protocols
through a unified interface.
"""

from .services.multi_service import MultiDeviceService
from .base.device import BaseDevice
from .base.interface import BaseInterface
from .base.register import BaseRegister, RegisterType

# Version of the devint package
__version__ = "0.1.0"

__all__ = [
    'MultiDeviceService',
    'BaseDevice',
    'BaseInterface',
    'BaseRegister',
    'RegisterType',
    '__version__',
]