#!/usr/bin/env python3
"""
modapi.cli - Direct command-line interface for Modbus API
"""

import os
import sys
import argparse

from .client import ModbusClient, auto_detect_modbus_port

def main():
    """Main entry point for the direct CLI"""
    parser = argparse.ArgumentParser(description='modapi - Direct Modbus API commands')
    parser.add_argument('--port', help='Modbus serial port')
    parser.add_argument('--baud', type=int, help='Baud rate')
    parser.add_argument('--timeout', type=float, help='Timeout in seconds')
    parser.add_argument('--unit', type=int, default=1, help='Modbus unit ID')
    parser.add_argument('command', help='Command: wc (write coil), rc (read coil), etc.')
    parser.add_argument('address', type=int, help='Register address')
    parser.add_argument('value', nargs='?', help='Value for write commands')
    parser.add_argument('count', nargs='?', type=int, help='Count for read commands')
    
    args = parser.parse_args()
    
    # Initialize client
    port = args.port
    if not port:
        port = auto_detect_modbus_port()
        if not port:
            print("Error: Could not auto-detect Modbus port")
            sys.exit(1)
    
    client = ModbusClient(
        port=port,
        baudrate=args.baud,
        timeout=args.timeout
    )
    
    if not client.connect():
        print(f"Error: Failed to connect to port {port}")
        sys.exit(1)
    
    try:
        # Process commands
        cmd = args.command.lower()
        
        if cmd == 'wc':  # Write coil
            if args.value is None:
                print("Error: Value required for write coil command")
                sys.exit(1)
                
            value = args.value.lower() in ('1', 'true', 'on', 'yes')
            result = client.write_coil(args.address, value, unit=args.unit)
            
            if result:
                print(f"Success: Wrote {'ON' if value else 'OFF'} to coil {args.address}")
            else:
                print(f"Error: Failed to write to coil {args.address}")
                sys.exit(1)
                
        elif cmd == 'rc':  # Read coil(s)
            count = args.count or 1
            result = client.read_coils(args.address, count, unit=args.unit)
            
            if result is not None:
                if count == 1:
                    print(f"Coil {args.address}: {'ON' if result[0] else 'OFF'}")
                else:
                    print(f"Coils {args.address}-{args.address + count - 1}:")
                    for i, val in enumerate(result):
                        print(f"  {args.address + i}: {'ON' if val else 'OFF'}")
            else:
                print(f"Error: Failed to read coil(s) at {args.address}")
                sys.exit(1)
                
        elif cmd == 'wh':  # Write holding register
            if args.value is None:
                print("Error: Value required for write holding register command")
                sys.exit(1)
                
            value = int(args.value)
            result = client.write_register(args.address, value, unit=args.unit)
            
            if result:
                print(f"Success: Wrote {value} to register {args.address}")
            else:
                print(f"Error: Failed to write to register {args.address}")
                sys.exit(1)
                
        elif cmd == 'rh':  # Read holding register(s)
            count = args.count or 1
            result = client.read_holding_registers(args.address, count, unit=args.unit)
            
            if result is not None:
                if count == 1:
                    print(f"Register {args.address}: {result[0]}")
                else:
                    print(f"Registers {args.address}-{args.address + count - 1}:")
                    for i, val in enumerate(result):
                        print(f"  {args.address + i}: {val}")
            else:
                print(f"Error: Failed to read register(s) at {args.address}")
                sys.exit(1)
                
        elif cmd == 'ri':  # Read input register(s)
            count = args.count or 1
            result = client.read_input_registers(args.address, count, unit=args.unit)
            
            if result is not None:
                if count == 1:
                    print(f"Input register {args.address}: {result[0]}")
                else:
                    print(f"Input registers {args.address}-{args.address + count - 1}:")
                    for i, val in enumerate(result):
                        print(f"  {args.address + i}: {val}")
            else:
                print(f"Error: Failed to read input register(s) at {args.address}")
                sys.exit(1)
                
        elif cmd == 'rd':  # Read discrete input(s)
            count = args.count or 1
            result = client.read_discrete_inputs(args.address, count, unit=args.unit)
            
            if result is not None:
                if count == 1:
                    print(f"Discrete input {args.address}: {'ON' if result[0] else 'OFF'}")
                else:
                    print(f"Discrete inputs {args.address}-{args.address + count - 1}:")
                    for i, val in enumerate(result):
                        print(f"  {args.address + i}: {'ON' if val else 'OFF'}")
            else:
                print(f"Error: Failed to read discrete input(s) at {args.address}")
                sys.exit(1)
                
        else:
            print(f"Error: Unknown command '{cmd}'")
            print("Available commands: wc, rc, wh, rh, ri, rd")
            sys.exit(1)
            
    finally:
        client.close()

if __name__ == '__main__':
    main()
