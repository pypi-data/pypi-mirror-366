"""
Modbus RTU package initialization
This package is a compatibility layer for the modapi.rtu module
"""

# Import from modapi.rtu
from modapi.rtu.client import ModbusRTUClient
from modapi.rtu.utils import find_serial_ports, test_modbus_port
from modapi.rtu.base import ModbusRTU
from modapi.rtu.protocol import (
    FUNC_READ_COILS, FUNC_READ_DISCRETE_INPUTS,
    FUNC_READ_HOLDING_REGISTERS, FUNC_READ_INPUT_REGISTERS,
    FUNC_WRITE_SINGLE_COIL, FUNC_WRITE_SINGLE_REGISTER,
    FUNC_WRITE_MULTIPLE_COILS, FUNC_WRITE_MULTIPLE_REGISTERS
)

# For backward compatibility
from modapi.rtu.utils import test_rtu_connection

# Export all symbols for backward compatibility
__all__ = [
    'ModbusRTU',
    'ModbusRTUClient',
    'find_serial_ports',
    'test_modbus_port',
    'test_rtu_connection',
    'FUNC_READ_COILS',
    'FUNC_READ_DISCRETE_INPUTS',
    'FUNC_READ_HOLDING_REGISTERS',
    'FUNC_READ_INPUT_REGISTERS',
    'FUNC_WRITE_SINGLE_COIL',
    'FUNC_WRITE_SINGLE_REGISTER',
    'FUNC_WRITE_MULTIPLE_COILS',
    'FUNC_WRITE_MULTIPLE_REGISTERS'
]
