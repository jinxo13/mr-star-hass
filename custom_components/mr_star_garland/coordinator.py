"""MyrtDesk update coordinator"""
import asyncio
from datetime import timedelta
from logging import Logger
from types import CoroutineType

from bleak import BleakClient
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)
from mr_star_ble import MrStarLight


class MrStarCoordinator(DataUpdateCoordinator):
    """MR Star device update coordinator"""
    _address: str
    _hass: HomeAssistant
    _ttl: int
    _connection_timeout: float
    _client: BleakClient | None
    _lock: asyncio.Lock
    _stopping: asyncio.Event
    _stopped: asyncio.Event
    _connected: asyncio.Event
    _logger: Logger

    def __init__(self, hass: HomeAssistant, logger: Logger, address: str, ttl: float):
        """Initialize MR Star coordinator."""
        super().__init__(
            hass,
            logger,
            name="mr_star",
            update_interval=timedelta(seconds=5),
        )
        self._hass = hass
        self._address = address
        self._ttl = ttl
        self._logger = logger
        self._lock = asyncio.Lock()
        self._stopping = asyncio.Event()
        self._stopped = asyncio.Event()
        self._connected = asyncio.Event()
        self._client = None

    @property
    async def connected(self):
        """Wait for connection status between this client and the Mr Star device."""
        await self._connected.wait()

    async def __aenter__(self):
        self._logger.debug("Acquiring lock")
        await self._lock.acquire()
        if not self.is_connected:
            self._logger.debug("No connection to device")
            return None
        return MrStarLight(self._client)

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._lock.release()

    @property
    def is_connected(self) -> bool:
        """Check connection status between this client and the Mr Star device."""
        return self._client is not None and self._client.is_connected and self._connected.is_set()

    async def start(self, await_connected: bool = True,
                      connection_timeout: float = 30):
        """Start the keep alive task."""
        self._connection_timeout = connection_timeout
        self._stopped.clear()
        asyncio.create_task(self._keep_alive())
        if await_connected:
            await self._connected.wait()

    async def stop(self):
        """Stop the keep alive task."""
        self._stopping.set()
        await self._stopped.wait()

    def create_on_connect_task(self, initialize: CoroutineType) -> None:
        """Create a task to update the state when the device is connected."""
        async def update_state():
            await self.connected
            await initialize

        asyncio.create_task(update_state())

    async def _keep_alive(self):
        """Keep alive task."""
        while True:
            async with self._lock:
                if self.is_connected:
                    await self._client.disconnect()
                    self._connected.clear()
                try:
                    ble_device = bluetooth.async_ble_device_from_address(
                        self._hass, self._address.upper())
                    self._client = BleakClient(ble_device)
                    await self._client.connect(timeout=self._connection_timeout)
                    self._connected.set()
                except Exception as exc:
                    self._logger.error("Error connecting to device: %s", exc)
                    await asyncio.sleep(15)
                    continue
            try:
                async with asyncio.timeout(self._ttl):
                    await self._stopping.wait()
                    await self._client.disconnect()
                    self._connected.clear()
                    self._stopped.set()
                    self._logger.debug("Disconnected from device %s", self._address)
                    break
            except asyncio.TimeoutError:
                self._logger.debug("Session timeout for device %s", self._address)


    async def _async_update_data(self):
        return {
            "connected": self.is_connected
        }
