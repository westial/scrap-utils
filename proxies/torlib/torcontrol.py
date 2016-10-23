import subprocess

import time

from proxies.settings import *


class TorControl(object):

    DELAY_SEC = 5

    def __init__(
            self,
            data_dir,
            address,
            port=15000,
            socks_port=9050,
            **kwargs
    ):
        self._address = address
        self._data_dir = data_dir
        self._port = port
        self._socks_port = socks_port
        self._kwargs = kwargs

    @property
    def data_dir(self):
        return self._data_dir

    @property
    def address(self):
        return self._address

    @property
    def port(self):
        return self._port

    @property
    def socks_port(self):
        return self._socks_port

    def _start_tor(self):
        subprocess.Popen(
            [
                "{!s}/{!s}".format(SH_TOR_DIR, SH_TOR_START),
                str(self._port),
                str(self._socks_port),
                self._data_dir
            ]
        )
        time.sleep(self.DELAY_SEC)

    def _exit_tor(self):
        subprocess.Popen(
            [
                "{!s}/{!s}".format(SH_TOR_DIR, SH_TOR_EXIT),
                str(self._port)
            ]
        )
        time.sleep(self.DELAY_SEC)

    def __enter__(self):
        self._start_tor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._exit_tor()
