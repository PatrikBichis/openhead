"""Find heads on the local network over mDNS (`_openhead._tcp`)."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass

from ..protocol import SERVICE_TYPE


@dataclass(frozen=True)
class DeviceInfo:
    name: str
    host: str
    port: int

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


async def discover(timeout: float = 2.0) -> list[DeviceInfo]:
    from zeroconf import ServiceStateChange
    from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

    names: set[str] = set()

    def on_change(zeroconf: object, service_type: str, name: str,
                  state_change: ServiceStateChange) -> None:
        if state_change in (ServiceStateChange.Added, ServiceStateChange.Updated):
            names.add(name)

    azc = AsyncZeroconf()
    browser = AsyncServiceBrowser(azc.zeroconf, [SERVICE_TYPE], handlers=[on_change])
    try:
        await asyncio.sleep(timeout)
        found = []
        for name in sorted(names):
            info = AsyncServiceInfo(SERVICE_TYPE, name)
            if await info.async_request(azc.zeroconf, 1000) and info.addresses:
                host = socket.inet_ntoa(info.addresses[0])
                found.append(DeviceInfo(name.removesuffix(f".{SERVICE_TYPE}"), host, info.port))
        return found
    finally:
        await browser.async_cancel()
        await azc.async_close()


async def resolve_device(device: str) -> tuple[str, int]:
    """`host[:port]` as given, or `auto`: the single head found over mDNS."""
    from .head import parse_address

    if device != "auto":
        return parse_address(device)
    devices = await discover(2.0)
    if len(devices) == 1:
        return devices[0].host, devices[0].port
    if not devices:
        raise ConnectionError("no head found over mDNS; pass --device host[:port]")
    names = ", ".join(f"{d.name} ({d.address})" for d in devices)
    raise ConnectionError(f"several heads found: {names}; pass --device")
