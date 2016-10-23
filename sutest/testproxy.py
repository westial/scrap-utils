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
        data_dir_ca = "/home/jaume/Documents/workspace/scrap-utils" \
                      "/proxies/torlib/data-ca"
        requester = Requester(host=GET_IP_URL, force_ssl=True)
        response = requester.open_request()
        home_ip = requester.read_response(response=response)
        proxy = TorProxy(
            data_dir=data_dir_ca,
            address='127.0.0.1',
            port=15000,
            socks_port=9050
        )
        requester = Requester(
            host=GET_IP_URL,
            force_ssl=True,
            proxies=proxy.proxy_config
        )
        response = requester.open_request()
        proxy_ip = requester.read_response(response=response)
        self.assertNotEqual(home_ip, proxy_ip, 'Different IP')

if __name__ == '__main__':
    unittest.main()
