"""Function test methods testing the image samples
"""
import unittest

from requester.Requester import Requester


class TestCases(unittest.TestCase):

    def setUp(self):
        self.submit_content = 'OK'
        self.url = 'https://localhost/test/scrap-utils/form.php'
        self.default_referer = 'http://leadtech.com'
        self.accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self.content_type = "application/json"

    def test_steps_sequence(self):
        requester = Requester(
            host=self.url,
            referer=self.default_referer,
            accept=self.accept,
            force_ssl=True)

        # Get page and cookie
        response = requester.open_request()

        self.assertEqual(response.status, 200)

        # Submit form with cookie
        post_fields = {
            'text_field': self.submit_content,
            'submit': 'Submit'
        }
        response = requester.open_request(
            post_fields=post_fields,
            redirect_reuse=True
        )
        result = requester.read_response(response=response)

        self.assertEqual(result, self.submit_content)

if __name__ == '__main__':
    unittest.main()
