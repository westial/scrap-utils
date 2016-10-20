#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script to test the requesting POST mode with unverifiable ssl support.
#
# This script uses the php form located into current directory. The php form
# must be able to execute by the web server. And the web address must be
# configured according to the php form destination.
#

from __future__ import absolute_import
from __future__ import print_function
from requester.Requester import Requester

EXPECTED_RESULT = 'OK'

print('Submitting php form...')

requester = Requester(host='https://localhost/test/scrap-utils/form.php',
                      referer='http://leadtech.com',
                      accept='text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                      force_ssl=True)

post_fields = {
    'text_field': EXPECTED_RESULT,
    'submit': 'Submit'
}

response = requester.open_request(post_fields=post_fields)

result = requester.read_response(response=response)

if result != EXPECTED_RESULT:
    print('ERROR: Result is not as expected.')
    exit(1)

else:
    print('SUCCESS: Result is "{!s}" as expected'.format(result))
    exit(0)

