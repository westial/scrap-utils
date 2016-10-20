"""Function test methods testing the image samples
"""
import sys
from _thread import start_new_thread

import time

from proxies.torproxy import TorProxy

sys.path.append('..')
import unittest

from requester.Requester import Requester

GET_IP_URL = 'https://api.ipify.org/'


class TestProxy(unittest.TestCase):

    def test_check_ip_after(self):
        requester = Requester(host=GET_IP_URL, force_ssl=True)
        response = requester.open_request()
        home_ip = requester.read_response(response=response)
        proxies = self._start_proxy(9153)
        start_new_thread(self._request_through_proxy, (proxies,))

    def _request_through_proxy(self, proxies):
        requester = Requester(
            host=GET_IP_URL,
            force_ssl=True,
            proxies=proxies
        )
        response = requester.open_request()
        self._proxy_ip = requester.read_response(response=response)

    @classmethod
    def _start_proxy(cls, socks_port):
        proxy = TorProxy(host='127.0.0.1', socks_port=socks_port)
        return proxy.proxy_config

if __name__ == '__main__':
    unittest.main()
