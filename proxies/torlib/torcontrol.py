import os
import subprocess

import time

from proxies.settings import *


class TorControl(object):

    DELAY_SEC = 5

    def __init__(
            self,
            data_dir_root,
            address,
            port=15000,
            socks_port=9050,
            exit_nodes: str = None,
            tor_scripts_dir=None,
            **kwargs
    ):
        self._tor_scripts_dir = self._get_tor_scripts_dir(tor_scripts_dir)
        self._address = address
        self._data_dir_root = data_dir_root
        self._port = port
        self._socks_port = socks_port
        self._exit_nodes = exit_nodes
        self._kwargs = kwargs

    @classmethod
    def _get_tor_scripts_dir(cls, tor_scripts_dir):
        if tor_scripts_dir and os.path.isdir(tor_scripts_dir):
            return tor_scripts_dir
        return SH_TOR_DIR

    def _build_exit_nodes(self):
        return ','.join(self._exit_nodes)

    @property
    def data_dir(self):
        return self._data_dir_root

    @property
    def address(self):
        return self._address

    @property
    def port(self):
        return self._port

    @property
    def socks_port(self):
        return self._socks_port

    def start(self):
        args = [
                "{!s}/{!s}".format(self._tor_scripts_dir, SH_TOR_START),
                str(self._port),
                str(self._socks_port),
                self._data_dir_root
            ]
        if self._exit_nodes:
            args.append(self._build_exit_nodes())
        subprocess.Popen(args)
        time.sleep(self.DELAY_SEC)

    def exit(self):
        subprocess.Popen(
            [
                "{!s}/{!s}".format(self._tor_scripts_dir, SH_TOR_EXIT),
                str(self._port)
            ]
        )
        time.sleep(self.DELAY_SEC)
