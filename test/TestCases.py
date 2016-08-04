"""Function test methods testing the image samples
"""
import sys
sys.path.append('..')
import unittest

from requester.Requester import Requester

ROOT_URL_TEST = 'https://localhost/test/scrap-utils'


class TestCases(unittest.TestCase):

    def setUp(self):
        self.submit_content = 'OK'
        self.url_form = '{!s}/form.php'.format(ROOT_URL_TEST)
        self.url_json = '{!s}/json.php'.format(ROOT_URL_TEST)
        self.default_referer = 'http://leadtech.com'
        self.accept = 'text/html,application/xhtml+xml,application/xml;' \
                      'q=0.9,*/*;q=0.8'
        self.content_type_json = "application/json; charset=utf-8"
        self.content_type_www = "application/x-www-form-urlencoded"

    def test_steps_sequence(self):
        requester = Requester(
            host=self.url_form,
            referer=self.default_referer,
            accept=self.accept,
            force_ssl=True)

        requester.update_headers({'Content-Type': self.content_type_www})

        # Get page and cookie
        response = requester.open_request()

        self.assertEqual(response.status_code, 200)

        # Submit form with cookie
        post_fields = {
            'text_field': self.submit_content,
            'submit': 'Submit'
        }
        response = requester.open_request(
            post_fields=post_fields
        )
        result = requester.read_response(response=response)

        self.assertEqual(result, self.submit_content)

    def test_post_json(self):
        requester = Requester(
            host=self.url_json,
            referer=self.default_referer,
            accept=self.accept,
            force_ssl=True)

        # requester.update_headers({'Content-Type': self.content_type_json})

        # Submit form with json field
        post_fields = {
            'result': self.submit_content
        }
        response = requester.open_request(
            post_fields=post_fields
        )
        result = requester.read_response(response=response)

        self.assertEqual(result, self.submit_content)

    def test_get_with_proxy(self):
        # ZAP or other proxy on port 8080 must be started before
        requester = Requester(
            host='http://docs.python-requests.org/en/master/user/advanced/',
            referer=self.default_referer,
            accept=self.accept,
            force_ssl=True,
            proxies={'http': 'localhost:8080', 'https': 'localhost:8080'}
        )

        response = requester.open_request()

        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
