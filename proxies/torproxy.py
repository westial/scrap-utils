"""
Proxy provider based on tor controller. First you need to start at least one
instance of tor and provide the configuration to this constructor.

Check https://github.com/jseidl/Multi-TOR for multiple tor instances.
"""
import time

import stem
from stem.control import Controller

from proxies.superproxy import Proxy


class TorProxy(Proxy):

    def __init__(self, host, port: int, **tor_kwargs):
        self._host = host
        self._control_port = port
        self._tor_kwargs = tor_kwargs
        self._tor = None

    class TorControl(object):

        def __init__(
                self,
                port=15001,
                address='127.0.0.1',
                socks_port=9051,
                exit_nodes: list=None
        ):
            self._address = address
            self._port = port
            self._socks_port = socks_port
            self._exit_nodes = exit_nodes

        @property
        def address(self):
            return self._address

        @property
        def port(self):
            return self._port

        @property
        def socks_port(self):
            return self._socks_port

        def _set_exit_nodes(self):
            if self._exit_nodes:
                conf_value = ','.join(self._exit_nodes)
                conf_value = '{{!s}}'.format(conf_value)
                self._controller.set_conf('ExitNodes', conf_value)

        def __enter__(self):
            try:
                self._controller = Controller.from_port(
                    address=self._address,
                    port=self._port
                )
                # HERE: https://stem.torproject.org/faq.html#how-do-i-request-a-new-identity-from-tor
                self._controller.authenticate()
                self._set_exit_nodes()

            except stem.SocketError as exc:
                raise ConnectionError(
                    "Unable to connect tor on control port {!s}: {!s}".format(
                        self._port,
                        str(exc)
                    )
                )
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self._controller.close()

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
        with self.TorControl(
                address=self._host,
                port=self._control_port,
                **self._tor_kwargs
        ) as self._tor:
            return self._build_config()
