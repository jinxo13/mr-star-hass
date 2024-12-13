"""Config flow for GenericBT integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from bleak import BleakClient, BLEDevice
from bleak.exc import BleakDeviceNotFoundError
from bluetooth_data_tools import human_readable_name
from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult
from mr_star_ble.const import LIGHT_SERVICE

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Generic BT."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak) -> FlowResult:
        """Handle the bluetooth discovery step."""
        if LIGHT_SERVICE not in discovery_info.service_uuids:
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {
            "name": human_readable_name(None, discovery_info.name, discovery_info.address)}
        return await self.async_step_user()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the user step to pick discovered device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            discovery_info = self._discovered_devices[address]
            local_name = discovery_info.name
            await self.async_set_unique_id(discovery_info.address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            try:
                await self._async_assert_device(discovery_info.device)
            except BleakDeviceNotFoundError:
                errors["base"] = "device_not_found"
            except Exception as exc:
                errors["base"] = "unknown_error"
                _LOGGER.error("Unexpected error: %s", exc)
            else:
                return self.async_create_entry(
                    title=local_name,
                    data={CONF_ADDRESS: discovery_info.address})

        if discovery := self._discovery_info:
            self._discovered_devices[discovery.address] = discovery
        else:
            current_addresses = self._async_current_ids()
            for discovery in async_discovered_service_info(self.hass):
                if (
                    discovery.address in current_addresses
                    or discovery.address in self._discovered_devices
                    or LIGHT_SERVICE not in discovery.service_uuids
                ):
                    continue
                self._discovered_devices[discovery.address] = discovery

        if not self._discovered_devices:
            return self.async_abort(reason="devices_not_found")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): vol.In(
                    {
                        service_info.address: (f"{service_info.name} ({service_info.address})")
                        for service_info in self._discovered_devices.values()
                    }
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def _async_assert_device(self, device: BLEDevice) -> bool:
        client = BleakClient(device)
        try:
            await client.connect(timeout=30)
            await client.disconnect()
            return True
        except Exception:
            return False
