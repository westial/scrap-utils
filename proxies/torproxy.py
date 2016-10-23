"""
Proxy provider based on tor controller. First you need to start at least one
instance of tor and provide the configuration to this constructor.

Check https://github.com/jseidl/Multi-TOR for multiple tor instances.
"""
import time

import stem
from stem.control import Controller

from proxies.superproxy import Proxy
from proxies.torlib.torcontrol import TorControl


class TorProxy(Proxy):

    def __init__(
            self,
            address,
            data_dir,
            port: int,
            socks_port: int,
            **tor_kwargs
    ):
        self._address = address
        self._data_dir = data_dir
        self._control_port = port
        self._socks_port = socks_port
        self._tor_kwargs = tor_kwargs
        self._tor = None

    def _build_config(self):
        return {
            'http': 'socks5://{!s}:{!s}'.format(
                self._tor.address,
                self._tor.socks_port
            ),
            'https': 'socks5://{!s}:{!s}'.format(
                self._tor.address,
                self._tor.socks_port
            )
        }

    @property
    def proxy_config(self):
        with TorControl(
                address=self._address,
                data_dir=self._data_dir,
                port=self._control_port,
                socks_port=self._socks_port,
                **self._tor_kwargs
        ) as self._tor:
            return self._build_config()
