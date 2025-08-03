import socket
import contextlib
import psutil
import typing as T

import websockets


class port_manager():
    """Manage the port usage.

    Use port_manager.get_port() to get a free port.
    """

    used_port: T.Set[int] = set()

    @classmethod
    def get_port(cls) -> int:
        while True:
            port = cls.find_free_port()
            if port in cls.used_port:  # pragma: no cover
                continue
            else:
                cls.consume_port(port)
                return port

    @classmethod
    def consume_port(cls, port: int):
        cls.used_port.add(port)

    @classmethod
    def release_port(cls, port: int):
        cls.used_port.remove(port)

    @staticmethod
    def find_free_port() -> int:
        """https://stackoverflow.com/a/45690594/8500469"""
        with contextlib.closing(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            port = s.getsockname()[1]
        return port

    @staticmethod
    def process_has_port(target_pid: int, ip: str, port: int) -> bool:
        p = psutil.Process(target_pid)
        addrs = [
            (c.laddr.ip, c.laddr.port) for c in p.connections()
        ]
        return (ip, port) in addrs


get_free_port = port_manager.get_port


def get_ip_addresses(ipv6: bool = False) -> dict:
    """Get the ip addresses of the machine.

    Args:
        ipv6 (bool, optional): Whether to include ipv6 addresses.
            Defaults to False.

    Returns:
        dict: The ip addresses of the machine.
    """
    ip_addresses = {}
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if (addr.family == socket.AF_INET) and (not ipv6):
                ip_addresses[iface] = addr.address
            elif (addr.family == socket.AF_INET6) and ipv6:
                ip_addresses[f"{iface} (IPv6)"] = addr.address
    return ip_addresses


WS_MAX_SIZE = 2**60
PING_INTERVAL = 20
PING_TIMEOUT = 120


def ws_connect(
    uri: str,
    max_size: int = WS_MAX_SIZE,
    ping_interval: int = PING_INTERVAL,
    ping_timeout: int = PING_TIMEOUT,
    **kwargs,
):
    return websockets.connect(
        uri,
        max_size=max_size,
        ping_interval=ping_interval,
        ping_timeout=ping_timeout,
        **kwargs,
    )


def ws_serve(
    handler,
    host: str = "localhost",
    port: int = 8765,
    max_size: int = WS_MAX_SIZE,
    ping_interval: int = PING_INTERVAL,
    ping_timeout: int = PING_TIMEOUT,
    **kwargs,
):
    return websockets.serve(
        handler,
        host,
        port,
        max_size=max_size,
        ping_interval=ping_interval,
        ping_timeout=ping_timeout,
        **kwargs,
    )
