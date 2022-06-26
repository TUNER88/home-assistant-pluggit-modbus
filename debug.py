#!/usr/bin/env python3
"""Pymodbus Synchronous Client Examples.

The following is an example of how to use the synchronous modbus client
implementation from pymodbus.

    with ModbusClient("127.0.0.1") as client:
        result = client.read_coils(1,10)
        print result
"""
import logging

# --------------------------------------------------------------------------- #
# import the various client implementations
# --------------------------------------------------------------------------- #
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

# from pymodbus.client.sync import ModbusUdpClient as ModbusClient
# from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# --------------------------------------------------------------------------- #
# configure the client logging
# --------------------------------------------------------------------------- #
FORMAT = (
    "%(asctime)-15s %(threadName)-15s "
    "%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

UNIT = 0x1


def run_sync_client():
    """Run sync client."""
    # ------------------------------------------------------------------------#
    # choose the client you want
    # ------------------------------------------------------------------------#
    # make sure to start an implementation to hit against. For this
    # you can use an existing device, the reference implementation in the tools
    # directory, or start a pymodbus server.
    #
    # If you use the UDP or TCP clients, you can override the framer being used
    # to use a custom implementation (say RTU over TCP). By default they use
    # the socket framer::
    #
    #    client = ModbusClient("localhost", port=5020, framer=ModbusRtuFramer)
    #
    # It should be noted that you can supply an ipv4 or an ipv6 host address
    # for both the UDP and TCP clients.
    #
    # There are also other options that can be set on the client that controls
    # how transactions are performed. The current ones are:
    #
    # * retries - Specify how many retries to allow per transaction (default=3)
    # * retry_on_empty - Is an empty response a retry (default = False)
    # * source_address - Specifies the TCP source address to bind to
    # * strict - Applicable only for Modbus RTU clients.
    #            Adheres to modbus protocol for timing restrictions
    #            (default = True).
    #            Setting this to False would disable the inter char timeout
    #            restriction (t1.5) for Modbus RTU
    #
    #
    # Here is an example of using these options::
    #
    #    client = ModbusClient("localhost", retries=3, retry_on_empty=True)
    # ------------------------------------------------------------------------#
    client = ModbusClient("192.168.1.19", port=502)
    # from pymodbus.transaction import ModbusRtuFramer
    # client = ModbusClient("localhost", port=5020, framer=ModbusRtuFramer)
    # client = ModbusClient(method="binary", port="/dev/ptyp0", timeout=1)
    # client = ModbusClient(method="ascii", port="/dev/ptyp0", timeout=1)
    # client = ModbusClient(method="rtu", port="/dev/ptyp0", timeout=1,
    #                       baudrate=9600)
    client.connect()



    log.debug("Read input registers")
    rr = client.read_holding_registers(133, 2, unit=UNIT)
    assert not rr.isError()  # nosec test that we are not an error
    
    decoder = BinaryPayloadDecoder.fromRegisters(rr.registers, Endian.Big, wordorder=Endian.Big)
    value = decoder.decode_32bit_float()
    log.debug("ZZZZZZZ")
    log.debug(value)



    # ----------------------------------------------------------------------- #
    # close the client
    # ----------------------------------------------------------------------- #
    client.close()


if __name__ == "__main__":
    run_sync_client()