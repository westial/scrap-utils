import time

from stem.process import launch_tor_with_config

from proxies.superproxy import Proxy


class TorProxy(Proxy):

    def __init__(self, host, socks_port, exit_nodes=None):
        self._host = host
        self._socks_port = str(socks_port)
        self._exit_nodes = exit_nodes
        self._tor = None

    class Tor(object):

        def __init__(self, socks_port, exit_nodes=None, start_delay=10):
            self._tor_process = None
            tor_config = {
                'ControlPort': '9159',
                'SocksPort': socks_port,
                'ExitNodes': '{ru}'
            }
            self._tor_process = launch_tor_with_config(
                config=tor_config,
                tor_cmd='/usr/local/bin/tor',
                take_ownership=True
            )
            time.sleep(start_delay)
            if self._tor_process > 0:
                print('TOR process PID {!s}'.format(self._tor_process.pid))
            else:
                raise ConnectionError('Unable to launch Tor instance')

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self._tor_process.kill()

    def _build_config(self):
        return {
            'http': 'socks5://{!s}:{!s}'.format(self._host, self._socks_port),
            'https': 'socks5://{!s}:{!s}'.format(self._host, self._socks_port)
        }

    @property
    def proxy_config(self):
        with self.Tor(
                socks_port=self._socks_port,
                exit_nodes=self._exit_nodes
        ) as self._tor:
            return self._build_config()
