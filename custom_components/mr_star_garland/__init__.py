"""Support for generic bluetooth devices."""

from logging import getLogger

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import MrStarCoordinator

PLATFORMS = [Platform.NUMBER, Platform.LIGHT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Generic BT from a config entry."""
    assert entry.unique_id is not None
    hass.data.setdefault(DOMAIN, {})
    address: str = entry.data[CONF_ADDRESS]
    coordinator = MrStarCoordinator(hass, getLogger(__name__), address, 120)
    await coordinator.start(await_connected=False, connection_timeout=30)
    device_id = address[len(address)-5:].replace(":", "")
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "info": {
            "identifiers": {
                (DOMAIN, entry.unique_id)
            },
            "name": f"Garland {device_id}",
            "manufacturer": "MR Star",
            "model": "Curtain",
        },
        "id": device_id
    }

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator: MrStarCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        await coordinator.stop()
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.config_entries.async_entries(DOMAIN):
            hass.data.pop(DOMAIN)

    return unload_ok
