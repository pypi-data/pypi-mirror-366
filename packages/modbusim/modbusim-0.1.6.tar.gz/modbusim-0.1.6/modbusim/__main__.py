"""Command-line interface for ModbusIM."""
import argparse
import logging
import sys
from typing import List, Optional

from .simulator import ModbusSimulator

def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Modbus Device Simulator")
    subparsers = parser.add_subparsers(dest="command", help="Modbus mode")
    
    # Common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--unit-id",
        type=int,
        default=1,
        help="Modbus unit ID (default: 1)",
    )
    parent_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    
    # RTU mode
    rtu_parser = subparsers.add_parser(
        "rtu",
        parents=[parent_parser],
        help="Run in RTU mode",
    )
    rtu_parser.add_argument(
        "--port",
        type=str,
        default="/tmp/ptyp0",
        help="Serial port (default: /tmp/ptyp0)",
    )
    rtu_parser.add_argument(
        "--baudrate",
        type=int,
        default=9600,
        help="Baud rate (default: 9600)",
    )
    rtu_parser.add_argument(
        "--timeout",
        type=float,
        default=0.1,
        help="Timeout in seconds (default: 0.1)",
    )
    
    # ASCII mode
    ascii_parser = subparsers.add_parser(
        "ascii",
        parents=[parent_parser],
        help="Run in ASCII mode",
    )
    ascii_parser.add_argument(
        "--port",
        type=str,
        default="/tmp/ptyp0",
        help="Serial port (default: /tmp/ptyp0)",
    )
    ascii_parser.add_argument(
        "--baudrate",
        type=int,
        default=9600,
        help="Baud rate (default: 9600)",
    )
    ascii_parser.add_argument(
        "--timeout",
        type=float,
        default=0.1,
        help="Timeout in seconds (default: 0.1)",
    )
    
    # TCP mode
    tcp_parser = subparsers.add_parser(
        "tcp",
        parents=[parent_parser],
        help="Run in TCP mode",
    )
    tcp_parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    tcp_parser.add_argument(
        "--port",
        type=int,
        default=5020,
        help="TCP port (default: 5020)",
    )
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> int:
    """Run the Modbus simulator.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parse_args(args)
    
    # Configure logging
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    if not parsed_args.command:
        print("Error: No mode specified. Use 'rtu', 'ascii', or 'tcp'.")
        return 1
    
    try:
        if parsed_args.command in ["rtu", "ascii"]:
            simulator = ModbusSimulator(
                mode=parsed_args.command,
                port=parsed_args.port,
                baudrate=parsed_args.baudrate,
                timeout=parsed_args.timeout,
                unit_id=parsed_args.unit_id,
            )
        else:  # TCP
            simulator = ModbusSimulator(
                mode="tcp",
                port=parsed_args.host,
                unit_id=parsed_args.unit_id,
            )
        
        # Set some test values
        simulator.set_values(0, [1, 0, 1, 0], "co")  # Coils 0-3
        simulator.set_values(0, [1234, 5678, 9012], "hr")  # Holding Registers 0-2
        
        print(f"Starting Modbus {parsed_args.command.upper()} simulator...")
        print(f"Test values set:")
        print(f"  - Coils 0-3: {simulator.get_values(0, 4, 'co')}")
        print(f"  - Holding Registers 0-2: {simulator.get_values(0, 3, 'hr')}")
        
        # Start the simulator and keep it running
        simulator.start()
        
        try:
            while True:
                # Keep the main thread alive
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            simulator.stop()
            return 0
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
