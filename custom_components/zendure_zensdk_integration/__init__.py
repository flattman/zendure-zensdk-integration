"""
Custom integration to integrate Zendure ZenSDK Integration with Home Assistant.

For more details about this integration, please refer to
https://github.com/flattman/zendure-zensdk-integration
"""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener

from .api import ZendureZensdkIntegrationApiClient
from .const import (
    CONF_MODEL,
    CONF_SERIAL_NUMBER,
    CONF_UPDATE_INTERVAL,
    DATA_KEY,
    DEFAULT_UPDATE_INTERVAL,
    DEVICE_MANUFACTURER,
    DOMAIN,
    PLATFORMS,
    MODEL_SOLARFLOW800,
)
from .const import STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class ZeroconfListener(ServiceListener):
    def __init__(self, service_type, expected_name):
        self.service_type = service_type
        self.expected_name = expected_name
        self.resolved_ip = None
        self.resolved_port = None
        self.event = asyncio.Event()

    def service_added(self, zeroconf, type, name):
        pass

    def service_removed(self, zeroconf, type, name):
        pass

    def service_updated(self, zeroconf, type, name):
        if type == self.service_type and name == self.expected_name + ".local.":
            info = zeroconf.get_service_info(type, name)
            if info:
                self.resolved_ip = info.address
                self.resolved_port = info.port
                self.event.set()



async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    serial_number = entry.data[CONF_SERIAL_NUMBER]
    model = entry.data[CONF_MODEL]
    update_interval = entry.options.get(
        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
    )

    mdns_name_base = f"Zendure-{model}-{serial_number}"
    service_type = "_http._tcp.local."
    expected_full_name = f"{mdns_name_base}"

    zeroconf_instance = Zeroconf()
    listener = ZeroconfListener(service_type, expected_full_name)
    browser = ServiceBrowser(zeroconf_instance, service_type, listener)

    try:
        await asyncio.wait_for(listener.event.wait(), timeout=5)  # Warte bis zu 5 Sekunden auf die Auflösung
        if listener.resolved_ip:
            ip_address = listener.resolved_ip.decode('utf-8')
            base_url = f"http://{ip_address}:{listener.resolved_port or 80}" # Standardmäßig Port 80 annehmen, falls nicht gefunden
            _LOGGER.debug(f"mDNS Name '{expected_full_name}' zu IP-Adresse '{ip_address}' aufgelöst.")

            session = async_get_clientsession(hass)
            client = ZendureZensdkIntegrationApiClient(model, serial_number, session)

            coordinator = ZendureZensdkIntegrationDataUpdateCoordinator(hass, client=client)
            await coordinator.async_refresh()

            if not coordinator.last_update_success:
                raise ConfigEntryNotReady

            hass.data[DOMAIN][entry.entry_id] = coordinator

            for platform in PLATFORMS:
                if entry.options.get(platform, True):
                    coordinator.platforms.append(platform)
                    hass.async_add_job(
                        hass.config_entries.async_forward_entry_setup(entry, platform)
                    )

            entry.add_update_listener(async_reload_entry)
            return True
        else:
            _LOGGER.error(f"mDNS Name '{expected_full_name}' konnte nicht aufgelöst werden.")
            return False
    except asyncio.TimeoutError:
        _LOGGER.error(f"Zeitüberschreitung bei der Auflösung des mDNS Namens '{expected_full_name}'.")
        return False
    finally:
        zeroconf_instance.close()


class ZendureZensdkIntegrationDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: ZendureZensdkIntegrationApiClient,
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
