"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/custom-components/integration_blueprint
"""
import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import device_registry as dr, entity_registry

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL

from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from .api import PluggitVentilationApiClient

from .const import (
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    port = entry.data[CONF_PORT]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]

    _LOGGER.debug("Setup %s.%s", DOMAIN, name)

    hub = PluggitVentilationApiClient(host, port)

    """Register the hub."""
    hass.data[DOMAIN][name] = {"hub": hub}

    # read serial number
    seriesnumber = "unknown"
    inverter_data = hub.read_holding_registers(unit=0x1, address=133, count=2)
    if inverter_data.isError():
        _LOGGER.error("cannot perform initial read for serial number")
    else:
        decoder = BinaryPayloadDecoder.fromRegisters(
            inverter_data.registers, Endian.Big, wordorder=Endian.Big
        )
        seriesnumber = decoder.decode_32bit_float()
        hub.seriesnumber = seriesnumber
    _LOGGER.info(f"serial number = {seriesnumber}")

    cust = hub.get_64bit_uint(4)
    _LOGGER.info(f"SER CUSTOM = {cust}")

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, cust)},
        manufacturer="Pluggit",
        model="P310",
        sw_version="1.0.0",
        hw_version="2.0.0",
        name=name,
    )

    return True


class BlueprintDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: PluggitVentilationApiClient
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api.async_get_data()
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
