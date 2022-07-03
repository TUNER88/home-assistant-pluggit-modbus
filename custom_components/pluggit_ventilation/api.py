"""Sample API Client."""
import logging
import asyncio
import socket
from typing import Optional
import aiohttp
import async_timeout
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant, callback
import threading
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

TIMEOUT = 10
UNIT = 0x1

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class PluggitVentilationApiClient:
    def __init__(self, host, port) -> None:
        """Modbus API Client."""
        _LOGGER.info("Create Pluggit modbus client")

        self._client = ModbusClient(host=host, port=port)
        self._lock = threading.Lock()

        self._host = host
        self._port = port
        self._sensors = []
        self.data = {}
        _LOGGER.info("Pluggit modbus client created %s", self.__dict__)

    @callback
    def async_add_pluggit_ventilation_sensor(self, update_callback):
        """Listen for data updates."""
        # This is the first sensor, set up interval.
        # _LOGGER.info(" This is the first sensor, set up interval.")

        self._sensors.append(update_callback)

    def read_holding_registers(self, unit, address, count):
        """Read holding registers."""
        with self._lock:
            kwargs = {"unit": unit} if unit else {}
            return self._client.read_holding_registers(address, count, **kwargs)

    def get_64bit_uint(self, register):
        response = self._client.read_holding_registers(register, 4, unit=UNIT)
        assert not response.isError()
        decoder = BinaryPayloadDecoder.fromRegisters(
            response.registers, Endian.Big, wordorder=Endian.Little
        )
        return decoder.decode_64bit_uint()

    def test_connection(self) -> bool:
        _LOGGER.info("Test connection")
        _LOGGER.info(self._host)
        client = ModbusClient(self._host, port=502)
        connected = client.connect()

        if connected:
            client.close()
            return True

        return False

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        return await self.api_wrapper("get", url)

    async def async_set_title(self, value: str) -> None:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        await self.api_wrapper("patch", url, data={"title": value}, headers=HEADERS)

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                if method == "get":
                    response = await self._session.get(url, headers=headers)
                    return await response.json()

                elif method == "put":
                    await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    await self._session.post(url, headers=headers, json=data)

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
