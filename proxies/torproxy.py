"""
Proxy provider based on tor controller. Tor command line application is mandatory.
"""
import time
from _thread import start_new_thread

from proxies.superproxy import Proxy
from proxies.torlib.torcontrol import TorControl


class TorProxy(Proxy):

    def __init__(
            self,
            address,
            data_dir_root,
            port: int,
            socks_port: int,
            exit_nodes: list=None,
            tor_scripts_dir=None,
            **tor_kwargs
    ):
        self._address = address
        self._data_dir_root = data_dir_root
        self._control_port = port
        self._socks_port = socks_port
        self._exit_nodes = exit_nodes
        self._tor_kwargs = tor_kwargs
        self._tor_scripts_dir = tor_scripts_dir
        self._tor = None
        self._alive = None

    def _build_config(self):
        while not self._tor:
            time.sleep(1)
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

    def _start_tor(self, *argv):
        self._tor = TorControl(
                data_dir_root=self._data_dir_root,
                address=self._address,
                port=self._control_port,
                socks_port=self._socks_port,
                exit_nodes=self._exit_nodes,
                tor_scripts_dir=self._tor_scripts_dir,
                **self._tor_kwargs
        )
        self._tor.start()
        self._alive = True
        while self._alive:
            time.sleep(1)

    def _exit_tor(self):
        self._tor.exit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._alive = False
        self._exit_tor()

    @property
    def proxy_config(self):
        start_new_thread(self._start_tor, (None,))
        return self._build_config()
