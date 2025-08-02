"""
Modbus RTU Protocol Module
Handles request building and response parsing for Modbus RTU
"""

import logging
import struct
import sys
from typing import Optional, List, Dict, Tuple

from .crc import calculate_crc, try_alternative_crcs
from modapi.config import (
    FUNC_READ_COILS, FUNC_READ_DISCRETE_INPUTS,
    FUNC_READ_HOLDING_REGISTERS, FUNC_READ_INPUT_REGISTERS,
    FUNC_WRITE_SINGLE_COIL, FUNC_WRITE_SINGLE_REGISTER,
    FUNC_WRITE_MULTIPLE_COILS, FUNC_WRITE_MULTIPLE_REGISTERS
)

logger = logging.getLogger(__name__)

# Waveshare-specific function codes
WAVESHARE_FUNC_READ_COILS = 0x41  # Sometimes used instead of 0x01
WAVESHARE_FUNC_FLASH_COIL = 0x05  # Same as write coil but with special register

# Exception codes
EXCEPTION_ILLEGAL_FUNCTION = 0x01
EXCEPTION_ILLEGAL_ADDRESS = 0x02
EXCEPTION_ILLEGAL_VALUE = 0x03
EXCEPTION_DEVICE_FAILURE = 0x04
EXCEPTION_ACKNOWLEDGE = 0x05
EXCEPTION_DEVICE_BUSY = 0x06
EXCEPTION_MEMORY_PARITY_ERROR = 0x08
EXCEPTION_GATEWAY_PATH_UNAVAILABLE = 0x0A
EXCEPTION_GATEWAY_TARGET_FAILED = 0x0B

# Exception code descriptions
EXCEPTION_DESCRIPTIONS = {
    EXCEPTION_ILLEGAL_FUNCTION: "Illegal function code",
    EXCEPTION_ILLEGAL_ADDRESS: "Illegal data address",
    EXCEPTION_ILLEGAL_VALUE: "Illegal data value",
    EXCEPTION_DEVICE_FAILURE: "Device failure",
    EXCEPTION_ACKNOWLEDGE: "Acknowledge",
    EXCEPTION_DEVICE_BUSY: "Device busy",
    EXCEPTION_MEMORY_PARITY_ERROR: "Memory parity error",
    EXCEPTION_GATEWAY_PATH_UNAVAILABLE: "Gateway path unavailable",
    EXCEPTION_GATEWAY_TARGET_FAILED: "Gateway target device failed to respond"
}

# Function code compatibility mapping for Waveshare devices
COMPATIBLE_FUNCTION_CODES = [
    # Standard Modbus compatible pairs
    (FUNC_READ_HOLDING_REGISTERS, FUNC_READ_INPUT_REGISTERS),
    # Waveshare-specific mappings
    (WAVESHARE_FUNC_READ_COILS, FUNC_READ_COILS),
    (FUNC_READ_COILS, WAVESHARE_FUNC_READ_COILS),
    (0x00, FUNC_READ_COILS),  # Some Waveshare devices respond with 0x00
    (0x00, FUNC_READ_DISCRETE_INPUTS),
    (0x00, FUNC_READ_HOLDING_REGISTERS),
    (0x00, FUNC_READ_INPUT_REGISTERS),
]

def build_request(unit_id: int, function_code: int, data: bytes) -> bytes:
    """
    Build Modbus RTU request frame
    
    Args:
        unit_id: Slave unit ID
        function_code: Modbus function code
        data: Request data
        
    Returns:
        bytes: Complete RTU frame with CRC
    """
    # Build request: [unit_id, function_code, data, crc_low, crc_high]
    request = bytes([unit_id, function_code]) + data
    crc = calculate_crc(request)
    # Append CRC in little-endian format (low byte first)
    request += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    
    logger.debug(f"Built request: {request.hex()}")
    return request

def parse_response(response: bytes, expected_unit: int, expected_function: int) -> Optional[bytes]:
    """
    Parse and validate Modbus RTU response
    
    This function handles Waveshare-specific quirks including:
    - CRC calculation variations
    - Function code mismatches
    - Unit ID mismatches (broadcast responses)
    
    Args:
        response: Raw response bytes
        expected_unit: Expected unit ID
        expected_function: Expected function code
        
    Returns:
        Optional[bytes]: Response data or None if invalid
    """
    # Check minimum length (unit_id + function_code + CRC)
    if len(response) < 4:
        logger.warning(f"Response too short: {response.hex()}")
        return None
    
    # Extract unit_id and function_code
    unit_id = response[0]
    function_code = response[1]
    
    # Check for exception response
    if function_code & 0x80:
        # Exception response format: [unit_id, function_code | 0x80, exception_code, crc]
        if len(response) >= 5:
            exception_code = response[2]
            exception_desc = EXCEPTION_DESCRIPTIONS.get(
                exception_code, f"Unknown exception code: {exception_code}"
            )
            logger.error(f"Modbus exception: {exception_desc} (code: {exception_code})")
        else:
            logger.error("Invalid exception response format")
        return None
    
    # Validate CRC
    is_valid_crc, _ = try_alternative_crcs(response)
    if not is_valid_crc:
        logger.warning(f"CRC validation failed for response: {response.hex()}")
        # For read operations with correct byte count, continue despite CRC errors
        if function_code in (FUNC_READ_COILS, FUNC_READ_DISCRETE_INPUTS, 
                            FUNC_READ_HOLDING_REGISTERS, FUNC_READ_INPUT_REGISTERS):
            if len(response) >= 3 and response[2] == len(response) - 5:  # Valid byte count
                logger.warning("Continuing despite CRC error - response structure appears valid")
            else:
                # For test environment, return None on CRC failure
                if "pytest" in sys.modules:
                    return None
                return None
        else:
            # For write operations, require valid CRC
            return None
    
    # Check unit ID match (allow broadcast address 0)
    if unit_id != expected_unit and unit_id != 0:
        logger.warning(f"Unit ID mismatch: expected {expected_unit}, got {unit_id}")
        # Continue anyway - some devices respond with incorrect unit ID
    
    # Check function code match
    if function_code != expected_function:
        logger.warning(f"Function code mismatch: expected {expected_function:02X}, got {function_code:02X}")
        
        # Check if the function codes are compatible
        is_compatible = False
        for fc1, fc2 in COMPATIBLE_FUNCTION_CODES:
            if (expected_function == fc1 and function_code == fc2) or \
               (expected_function == fc2 and function_code == fc1):
                logger.info(f"Function codes {expected_function:02X} and {function_code:02X} are compatible")
                is_compatible = True
                break
        
        if not is_compatible:
            # For Waveshare devices, sometimes they respond with a different function code
            # but the response is still valid. Log a warning but continue processing.
            logger.warning(f"Function code mismatch (but continuing): expected {expected_function:02X}, got {function_code:02X}")
            # Don't return None here, continue processing the response
            
            # If this is a write operation, the response should be an echo of the request
            if function_code in (FUNC_WRITE_SINGLE_COIL, FUNC_WRITE_SINGLE_REGISTER) and \
               len(response) >= 6:  # Minimum length for write response
                # The response should be an echo of the request
                # Return the response data without the CRC (first 2 bytes are unit_id and function_code)
                return response[2:-2]
            
            # For read operations, we'll continue with the response as is
    
    # Extract data (without unit_id, function_code, and CRC)
    data = response[2:-2]
    return data

def parse_read_coils_response(response_data: bytes) -> Optional[List[bool]]:
    """
    Parse response data for read coils/discrete inputs
    
    Args:
        response_data: Response data without header and CRC
        
    Returns:
        Optional[List[bool]]: List of coil states or None if error
    """
    if not response_data or len(response_data) < 1:
        return None
    
    byte_count = response_data[0]
    if len(response_data) < byte_count + 1:
        logger.error(f"Invalid read coils response: expected {byte_count} bytes, got {len(response_data)-1}")
        return None
    
    coil_bytes = response_data[1:byte_count+1]
    coils = []
    
    for byte_val in coil_bytes:
        for bit_pos in range(8):
            coil_state = bool(byte_val & (1 << bit_pos))
            coils.append(coil_state)
    
    return coils

def parse_read_registers_response(response_data: bytes) -> Optional[List[int]]:
    """
    Parse response data for read holding/input registers
    
    Args:
        response_data: Response data without header and CRC
        
    Returns:
        Optional[List[int]]: List of register values or None if error
    """
    if not response_data or len(response_data) < 1:
        return None
    
    byte_count = response_data[0]
    if len(response_data) < byte_count + 1:
        logger.error(f"Invalid read registers response: expected {byte_count} bytes, got {len(response_data)-1}")
        return None
    
    register_data = response_data[1:byte_count+1]
    registers = []
    
    # Each register is 2 bytes, big-endian
    for i in range(0, len(register_data), 2):
        if i + 1 < len(register_data):
            register_value = (register_data[i] << 8) | register_data[i+1]
            registers.append(register_value)
    
    return registers

def build_read_request(unit_id: int, function_code: int, address: int, count: int) -> bytes:
    """
    Build request for read functions (coils, discrete inputs, registers)
    
    Args:
        unit_id: Slave unit ID
        function_code: Function code (0x01, 0x02, 0x03, 0x04)
        address: Starting address
        count: Number of items to read
        
    Returns:
        bytes: Request data
    """
    # Data format: [address_high, address_low, count_high, count_low]
    data = struct.pack('>HH', address, count)
    return build_request(unit_id, function_code, data)

def build_write_single_coil_request(unit_id: int, address: int, value: bool) -> bytes:
    """
    Build request for write single coil
    
    Args:
        unit_id: Slave unit ID
        address: Coil address
        value: Coil value
        
    Returns:
        bytes: Request data
    """
    # Data format: [address_high, address_low, value_high, value_low]
    # Value is 0xFF00 for ON, 0x0000 for OFF
    coil_value = 0xFF00 if value else 0x0000
    data = struct.pack('>HH', address, coil_value)
    return build_request(unit_id, FUNC_WRITE_SINGLE_COIL, data)

def build_write_single_register_request(unit_id: int, address: int, value: int) -> bytes:
    """
    Build request for write single register
    
    Args:
        unit_id: Slave unit ID
        address: Register address
        value: Register value
        
    Returns:
        bytes: Request data
    """
    # Data format: [address_high, address_low, value_high, value_low]
    data = struct.pack('>HH', address, value)
    return build_request(unit_id, FUNC_WRITE_SINGLE_REGISTER, data)

def build_write_multiple_coils_request(unit_id: int, address: int, values: List[bool]) -> bytes:
    """
    Build request for write multiple coils
    
    Args:
        unit_id: Slave unit ID
        address: Starting address
        values: List of coil values
        
    Returns:
        bytes: Request data
    """
    count = len(values)
    byte_count = (count + 7) // 8  # Ceiling division
    
    # Pack coil values into bytes
    coil_bytes = bytearray(byte_count)
    for i, value in enumerate(values):
        if value:
            byte_index = i // 8
            bit_index = i % 8
            coil_bytes[byte_index] |= (1 << bit_index)
    
    # Data format: [address_high, address_low, count_high, count_low, byte_count, coil_bytes]
    data = struct.pack('>HHB', address, count, byte_count) + coil_bytes
    return build_request(unit_id, FUNC_WRITE_MULTIPLE_COILS, data)

def build_write_multiple_registers_request(unit_id: int, address: int, values: List[int]) -> bytes:
    """
    Build request for write multiple registers
    
    Args:
        unit_id: Slave unit ID
        address: Starting address
        values: List of register values
        
    Returns:
        bytes: Request data
    """
    count = len(values)
    byte_count = count * 2
    
    # Pack register values
    register_bytes = bytearray()
    for value in values:
        register_bytes.extend(struct.pack('>H', value))
    
    # Data format: [address_high, address_low, count_high, count_low, byte_count, register_bytes]
    data = struct.pack('>HHB', address, count, byte_count) + bytes(register_bytes)
    return build_request(unit_id, FUNC_WRITE_MULTIPLE_REGISTERS, data)
