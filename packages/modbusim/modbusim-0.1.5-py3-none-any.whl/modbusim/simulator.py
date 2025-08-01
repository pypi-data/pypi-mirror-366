"""
Modbus Device Simulator

This module provides a Modbus device simulator that can simulate both RTU and TCP devices.
"""
import logging
import threading
from typing import Dict, List, Optional, Union

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
    ModbusServerContext,
)
from pymodbus.server.sync import StartSerialServer, StartTcpServer
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer, ModbusTcpFramer


class ModbusSimulator:
    """A Modbus device simulator that can simulate both RTU and TCP devices.

    Args:
        mode: The Modbus mode ("rtu", "ascii", or "tcp")
        port: The serial port (for RTU/ASCII) or host (for TCP)
        baudrate: The baud rate (for RTU/ASCII)
        timeout: The timeout in seconds
        unit_id: The Modbus unit ID
        **kwargs: Additional keyword arguments for the Modbus server
    """

    def __init__(
        self,
        mode: str = "rtu",
        port: str = "/tmp/ptyp0",
        baudrate: int = 9600,
        timeout: float = 0.1,
        unit_id: int = 1,
        **kwargs,
    ):
        self.mode = mode.lower()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.unit_id = unit_id
        self.server = None
        self.server_thread = None
        self.running = False
        self.kwargs = kwargs

        # Initialize data stores
        self.store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0] * 100),  # Discrete Inputs
            co=ModbusSequentialDataBlock(0, [0] * 100),  # Coils
            hr=ModbusSequentialDataBlock(0, [0] * 100),  # Holding Registers
            ir=ModbusSequentialDataBlock(0, [0] * 100),  # Input Registers
        )

        self.context = ModbusServerContext(slaves={unit_id: self.store}, single=True)

        # Configure logging
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def set_values(
        self,
        address: int,
        values: List[Union[int, bool]],
        register_type: str = "co",
        unit_id: Optional[int] = None,
    ) -> None:
        """Set values in the Modbus device.

        Args:
            address: The starting address
            values: The values to set
            register_type: The type of register ("co", "di", "hr", "ir")
            unit_id: The unit ID (defaults to the instance's unit_id)
        """
        unit_id = unit_id or self.unit_id
        self.store.setValues(register_type, address, values)
        self.logger.info(
            "Set %s[%d:%d] = %s", register_type.upper(), address, address + len(values), values
        )

    def get_values(
        self,
        address: int,
        count: int = 1,
        register_type: str = "co",
        unit_id: Optional[int] = None,
    ) -> List[Union[int, bool]]:
        """Get values from the Modbus device.

        Args:
            address: The starting address
            count: The number of values to get
            register_type: The type of register ("co", "di", "hr", "ir")
            unit_id: The unit ID (defaults to the instance's unit_id)

        Returns:
            A list of values
        """
        unit_id = unit_id or self.unit_id
        return self.store.getValues(register_type, address, count)

    def _run_server(self):
        """Run the Modbus server in a separate thread."""
        try:
            if self.mode in ["rtu", "ascii"]:
                framer = ModbusRtuFramer if self.mode == "rtu" else ModbusAsciiFramer
                self.server = StartSerialServer(
                    context=self.context,
                    framer=framer,
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=self.timeout,
                    **self.kwargs,
                )
            else:  # TCP
                self.server = StartTcpServer(
                    context=self.context,
                    framer=ModbusTcpFramer,
                    address=(self.port, 5020),
                    **self.kwargs,
                )
        except Exception as e:
            self.logger.error("Error in Modbus server: %s", e)
            self.running = False

    def start(self) -> None:
        """Start the Modbus server in a separate thread."""
        if self.running:
            self.logger.warning("Server is already running")
            return

        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        self.logger.info(
            "Started Modbus %s server on %s",
            self.mode.upper(),
            self.port if self.mode != "tcp" else f"{self.port}:5020",
        )

    def stop(self) -> None:
        """Stop the Modbus server."""
        if not self.running:
            return

        self.running = False
        if self.server:
            self.server.server_close()
            self.server = None

        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=1.0)

        self.logger.info("Stopped Modbus %s server", self.mode.upper())

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
