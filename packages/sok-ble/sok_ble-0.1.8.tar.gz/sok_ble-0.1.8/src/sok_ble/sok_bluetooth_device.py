"""BLE device abstraction for SOK batteries."""

from __future__ import annotations

import asyncio
import logging
import statistics
import struct
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

import async_timeout
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

from sok_ble.const import UUID_RX, UUID_TX, _sok_command
from sok_ble.exceptions import BLEConnectionError
from sok_ble.sok_parser import SokParser

logger = logging.getLogger(__name__)

try:
    from bleak_retry_connector import (
        BleakClientWithServiceCache,
        establish_connection,
    )
except Exception:  # pragma: no cover - optional dependency
    from bleak import BleakClient as BleakClientWithServiceCache

    establish_connection = None  # type: ignore[misc]


class SokBluetoothDevice:
    """Minimal BLE interface for a SOK battery."""

    def __init__(
        self, ble_device: BLEDevice, adapter: Optional[str] | None = None
    ) -> None:
        self._ble_device = ble_device
        self._adapter = adapter

        self.voltage: float | None = None
        self.current: float | None = None
        self.soc: int | None = None
        self.temperature: float | None = None
        self.capacity: float | None = None
        self.num_cycles: int | None = None
        self.cell_voltages: list[float] | None = None

        # Housekeeping
        self.num_samples = 0

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator[BleakClientWithServiceCache]:
        """Connect to the device and yield a BLE client."""
        logger.debug("Connecting to %s", self._ble_device.address)
        last_err: Exception | None = None
        client: BleakClientWithServiceCache | None = None

        for attempt in range(3):
            try:
                if establish_connection:
                    client = await establish_connection(
                        BleakClientWithServiceCache,
                        self._ble_device,
                        self._ble_device.name or self._ble_device.address,
                        adapter=self._adapter,
                    )
                else:
                    client = BleakClientWithServiceCache(
                        self._ble_device,
                        adapter=self._adapter,
                    )
                    await client.connect()

                # Force service discovery
                async with async_timeout.timeout(5):
                    _ = client.services
                await asyncio.sleep(0.15)
                break
            except (BleakError, asyncio.TimeoutError) as err:
                last_err = err
                logger.debug(
                    "BLE connect attempt %s failed for %s: %s",
                    attempt + 1,
                    self._ble_device.address,
                    err,
                )
                await asyncio.sleep(0.5)
        else:
            raise BLEConnectionError(
                f"Unable to establish GATT connection to {self._ble_device.address}"
            ) from last_err

        assert client is not None
        try:
            yield client
        finally:
            await client.disconnect()
            logger.debug("Disconnected from %s", self._ble_device.address)

    async def _send_command(
        self, client: BleakClientWithServiceCache, cmd: int, expected: int
    ) -> bytes:
        """Send a command and return the response bytes with the given header."""

        for attempt in range(2):
            try:
                start_notify = getattr(client, "start_notify", None)
                if start_notify is None:
                    await client.write_gatt_char(UUID_TX, _sok_command(cmd))
                    data = bytes(await client.read_gatt_char(UUID_RX))
                    return data

                queue: asyncio.Queue[bytes] = asyncio.Queue()

                def handler(_: int, data: bytearray) -> None:
                    queue.put_nowait(bytes(data))

                await client.start_notify(UUID_RX, handler)
                try:
                    await client.write_gatt_char(UUID_TX, _sok_command(cmd))
                    while True:
                        data = await asyncio.wait_for(queue.get(), 5.0)
                        if struct.unpack_from(">H", data)[0] == expected:
                            return data
                finally:
                    await client.stop_notify(UUID_RX)
            except BleakError as err:
                if attempt == 0:
                    logger.debug(
                        "BLE command attempt failed for %s: %s",
                        self._ble_device.address,
                        err,
                    )
                    await asyncio.sleep(0.2)
                    continue
                raise

    async def async_update(self) -> None:
        """Poll the device for all telemetry and update attributes."""
        responses: dict[int, bytes] = {}
        async with self._connect() as client:
            logger.debug("Send C1")
            data = await self._send_command(client, 0xC1, 0xCCF0)
            logger.debug(
                "Recv 0x%04X: %s",
                struct.unpack_from(">H", data)[0],
                data.hex(),
            )
            responses[0xCCF0] = data

            logger.debug("Send C1")
            data = await self._send_command(client, 0xC1, 0xCCF2)
            logger.debug(
                "Recv 0x%04X: %s",
                struct.unpack_from(">H", data)[0],
                data.hex(),
            )
            responses[0xCCF2] = data

            logger.debug("Send C2")
            data = await self._send_command(client, 0xC2, 0xCCF3)
            logger.debug(
                "Recv 0x%04X: %s",
                struct.unpack_from(">H", data)[0],
                data.hex(),
            )
            responses[0xCCF3] = data

            logger.debug("Send C2")
            data = await self._send_command(client, 0xC2, 0xCCF4)
            logger.debug(
                "Recv 0x%04X: %s",
                struct.unpack_from(">H", data)[0],
                data.hex(),
            )
            responses[0xCCF4] = data

        parsed = SokParser.parse_all(responses)
        logger.debug("Parsed update: %s", parsed)

        self.voltage = parsed["voltage"]
        self.current = parsed["current"]
        self.soc = parsed["soc"]
        self.temperature = parsed["temperature"]
        self.capacity = parsed["capacity"]
        self.num_cycles = parsed["num_cycles"]
        self.cell_voltages = parsed["cell_voltages"]

        self.num_samples += 1

    # Derived metrics -----------------------------------------------------

    @property
    def power(self) -> float | None:
        """Return instantaneous power in watts."""
        if self.voltage is None or self.current is None:
            return None
        return self.voltage * self.current

    @property
    def cell_voltage_max(self) -> float | None:
        cells = self.cell_voltages
        return max(cells) if cells else None

    @property
    def cell_voltage_min(self) -> float | None:
        cells = self.cell_voltages
        return min(cells) if cells else None

    @property
    def cell_voltage_avg(self) -> float | None:
        cells = self.cell_voltages
        if not cells:
            return None
        return sum(cells) / len(cells)

    @property
    def cell_voltage_median(self) -> float | None:
        cells = self.cell_voltages
        if not cells:
            return None
        return statistics.median(cells)

    @property
    def cell_voltage_delta(self) -> float | None:
        if self.cell_voltage_max is None or self.cell_voltage_min is None:
            return None
        return self.cell_voltage_max - self.cell_voltage_min

    @property
    def cell_index_max(self) -> int | None:
        cells = self.cell_voltages
        if not cells:
            return None
        return cells.index(max(cells))

    @property
    def cell_index_min(self) -> int | None:
        cells = self.cell_voltages
        if not cells:
            return None
        return cells.index(min(cells))
