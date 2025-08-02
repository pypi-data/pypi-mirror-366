"""
modapi - Main entry point for running as a module
"""

import os
import sys
import argparse
import logging
import json

from . import load_env_files
from .api.rest import create_rest_app
from .api.mqtt import start_mqtt_broker
from .api.shell import interactive_mode
from .api.cmd import execute_command
# Import Modbus-related functions from the rtu module
from .api.rtu import (
    find_serial_ports,
    test_modbus_port,
    test_rtu_connection,
    create_rtu_client
)

# Import configuration
from .config import PRIORITIZED_BAUDRATES
# Import configuration variables
from .config import BAUDRATES, PRIORITIZED_BAUDRATES, AUTO_DETECT_UNIT_IDS

def auto_detect_modbus_port(baudrates=None, debug=False, unit_id=None):
    """
    Auto-detect Modbus RTU port
    
    Args:
        baudrates: List of baud rates to try (default: [9600, 19200, 38400, 57600, 115200])
        debug: Enable debug output
        unit_id: Specific unit ID to test (default: None, tests unit ID 1)
        
    Returns:
        dict: Dictionary with port information if found, None otherwise
    """
    if baudrates is None:
        baudrates = PRIORITIZED_BAUDRATES
    
    ports = find_serial_ports()
    if debug:
        print(f"Scanning {len(ports)} serial ports...")
    
    for port in ports:
        if debug:
            print(f"\nChecking port: {port}")
        
        for baudrate in baudrates:
            if debug:
                print(f"  Trying baudrate: {baudrate}")
            
            try:
                # Test with the specified unit ID or default to 1
                test_unit_id = unit_id if unit_id is not None else 1
                if test_modbus_port(port, baudrate=baudrate, unit_id=test_unit_id):
                    if debug:
                        print(f"✅ Found Modbus device on {port} at {baudrate} baud")
                    return {
                        'port': port,
                        'baudrate': baudrate,
                        'unit_id': test_unit_id
                    }
            except Exception as e:
                if debug:
                    print(f"    Error: {str(e)}")
                continue
    
    return None

# Configure logging
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the modapi module"""
    # Load environment variables
    load_env_files()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='modapi - Unified API for Modbus communication')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # REST API command
    rest_parser = subparsers.add_parser('rest', help='Run REST API server')
    rest_parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server')
    rest_parser.add_argument('--port', type=int, default=int(os.environ.get('modapi_PORT', 5000)), 
                           help='Port to bind the server')
    rest_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    rest_parser.add_argument('--modbus-port', help='Modbus serial port')
    rest_parser.add_argument('--baudrate', type=int, help='Baud rate')
    rest_parser.add_argument('--timeout', type=float, help='Timeout in seconds')
    
    # MQTT command
    mqtt_parser = subparsers.add_parser('mqtt', help='Run MQTT client')
    mqtt_parser.add_argument('--broker', default=os.environ.get('MQTT_BROKER', 'localhost'), 
                           help='MQTT broker address')
    mqtt_parser.add_argument('--port', type=int, default=int(os.environ.get('MQTT_PORT', 1883)), 
                           help='MQTT broker port')
    mqtt_parser.add_argument('--topic-prefix', default=os.environ.get('MQTT_TOPIC_PREFIX', 'modapi'), 
                           help='MQTT topic prefix')
    mqtt_parser.add_argument('--modbus-port', help='Modbus serial port')
    mqtt_parser.add_argument('--baudrate', type=int, help='Baud rate')
    mqtt_parser.add_argument('--timeout', type=float, help='Timeout in seconds')
    
    # Shell command
    shell_parser = subparsers.add_parser('shell', help='Run interactive shell')
    shell_parser.add_argument('--modbus-port', help='Modbus serial port')
    shell_parser.add_argument('--baudrate', type=int, help='Baud rate')
    shell_parser.add_argument('--timeout', type=float, help='Timeout in seconds')
    shell_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    # Direct command execution
    cmd_parser = subparsers.add_parser('cmd', help='Execute Modbus command directly')
    cmd_parser.add_argument('--modbus-port', help='Modbus serial port')
    cmd_parser.add_argument('--baudrate', type=int, help='Baud rate')
    cmd_parser.add_argument('--timeout', type=float, help='Timeout in seconds')
    cmd_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    cmd_parser.add_argument('modbus_command', help='Command: wc (write coil), rc (read coil), etc.')
    cmd_parser.add_argument('args', nargs='*', help='Command arguments')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for Modbus devices')
    scan_parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    # Support both singular and plural forms for port/ports
    port_group = scan_parser.add_mutually_exclusive_group()
    port_group.add_argument('--port', help='Specify a specific port to test')
    port_group.add_argument('--ports', help='Specify comma-separated ports to test (e.g., /dev/ttyACM0,/dev/ttyUSB0)')
    
    # Support both singular and plural forms for baudrate/baudrates
    baudrate_group = scan_parser.add_mutually_exclusive_group()
    baudrate_group.add_argument('--baudrate', type=int, help='Specify a specific baud rate to test')
    baudrate_group.add_argument('--baudrates', help='Specify comma-separated baud rates to test (e.g., 9600,19200)')
    
    # Support both singular and plural forms for unit/unit-ids
    unit_group = scan_parser.add_mutually_exclusive_group()
    unit_group.add_argument('--unit', type=int, help='Specify a specific unit ID to test')
    unit_group.add_argument('--unit-ids', help='Specify comma-separated unit IDs to test (e.g., 1,2,3)')
    
    args = parser.parse_args()
    
    # Run the selected command
    if args.command == 'rest':
        app = create_rest_app(
            port=args.modbus_port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            host=args.host,
            api_port=args.port,
            debug=args.debug
        )
        app.run(host=args.host, port=args.port, debug=args.debug)
    elif args.command == 'mqtt':
        start_mqtt_broker(
            port=args.modbus_port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            broker=args.broker,
            mqtt_port=args.port,
            topic_prefix=args.topic_prefix
        )
    elif args.command == 'shell':
        # Run interactive shell
        interactive_mode(
            port=args.modbus_port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            verbose=args.verbose
        )
    elif args.command == 'cmd':
        # Execute command directly
        if not hasattr(args, 'modbus_command') or not args.modbus_command:
            print("Error: No Modbus command provided")
            sys.exit(1)
            
        # Pass the modbus_command and args to execute_command
        success, response = execute_command(
            command=args.modbus_command,
            args=args.args,
            port=args.modbus_port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            verbose=args.verbose
        )
        
        # Output response as JSON
        print(json.dumps(response, indent=2))
        
        # Exit with appropriate status code
        sys.exit(0 if success else 1)
    elif args.command == 'scan':
        # Configure logging based on debug flag
        if args.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
            logger.setLevel(logging.INFO)
            
        # Parse ports, baudrates, and unit IDs from arguments
        ports = []
        if args.port:
            ports = [args.port]
        elif args.ports:
            ports = args.ports.split(',')
        
        baudrates = PRIORITIZED_BAUDRATES
        if args.baudrate:
            baudrates = [args.baudrate]
        elif args.baudrates:
            try:
                baudrates = [int(b) for b in args.baudrates.split(',')]
            except ValueError:
                print("Error: Invalid baudrate format. Use comma-separated integers.")
                sys.exit(1)
        
        unit_ids = [1]  # Default unit ID
        if args.unit is not None:
            unit_ids = [args.unit]
        elif args.unit_ids:
            try:
                unit_ids = [int(u) for u in args.unit_ids.split(',')]
            except ValueError:
                print("Error: Invalid unit ID format. Use comma-separated integers.")
                sys.exit(1)
        
        # If specific ports are provided, test just those ports
        if ports:
            for port in ports:
                print(f"🔍 Testing specified port: {port}")
                
                for baudrate in baudrates:
                    print(f"  ⚙️  {baudrate} baud...")
                    
                    for unit_id in unit_ids:
                        print(f"    📟 Unit ID {unit_id}...", end=" ")
                        success, result = test_modbus_port(
                            port=port,
                            baudrate=baudrate,
                            unit_id=unit_id,
                            debug=args.debug
                        )
                        if success:
                            print("✅ Device found!")
                            if args.debug:
                                print(f"    Details: {result}")
                            sys.exit(0)
                        else:
                            if args.debug:
                                print(f"❌ {result.get('error', 'No response')}")
                            else:
                                print("❌")
                
                print(f"\n❌ No Modbus device found on {port} with the specified parameters")
            
            if len(ports) > 1:
                print(f"\n❌ No Modbus devices found on any of the specified ports: {', '.join(ports)}")
            else:
                print(f"\n❌ No Modbus device found on {ports[0]}")
            sys.exit(1)
        else:
            # Scan all ports
            result = auto_detect_modbus_port(
                baudrates=baudrates if baudrates != PRIORITIZED_BAUDRATES else None,
                debug=args.debug,
                unit_id=unit_ids[0] if unit_ids else None
            )
            if result:
                print(f"\n✅ Found Modbus device on {result.get('port')}")
                if args.debug:
                    print(f"    Details: {result}")
                sys.exit(0)
            else:
                print("\n❌ No Modbus devices found!")
                if args.debug:
                    print("    Make sure the device is properly connected and powered on.")
                    print("    Try specifying a different baud rate with --baudrate")
                    print("    or a specific unit ID with --unit")
                sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
