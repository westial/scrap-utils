#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Transmission class
#
from __future__ import absolute_import

import json
import re
import requests as requests
import urllib3


class Requester(object):
    """
    Transmission class.
    """

    DEFAULT_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130' \
                    '401 Firefox/31.0'

    DEFAULT_REFERER = 'http://www.westial.com'

    DEFAULT_ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,' \
                     '*/*;q=0.8'

    DEFAULT_LANG = "en-US,en;q=0.5"

    def __init__(self,
                 host=None,
                 agent=None,
                 referer=None,
                 accept=None,
                 lang=None,
                 force_ssl=None,
                 **kwargs):
        """
        Constructor
        
        :param agent: str HTTP Agent header
        :param referer: str HTTP Referer header
        :param accept: str HTTP Accept header
        :param force_ssl: bool bypass SSL verification
        """

        self._host = host
        self._agent = agent
        self._referer = referer
        self._accept = accept

        self._req_kwargs = kwargs

        if not agent:
            self._agent = self.DEFAULT_AGENT

        if not referer:
            self._referer = self.DEFAULT_REFERER

        if not accept:
            self._accept = self.DEFAULT_ACCEPT

        if not lang:
            self._lang = self.DEFAULT_LANG

        self._opener = None

        self._verify = not force_ssl

        self._session = requests.Session()

        self.update_headers(self._get_default_headers())

        pass

    def _is_content_type_json(self):
        pattern = '.*application/json(?:;.*|$)'
        headers_ = [
            'content-type',
            'Content-type',
            'Content-Type',
        ]
        return self.header_contains(headers_, pattern)

    def header_contains(self, headers_, pattern):
        while headers_:
            header = headers_.pop()
            if header in self.opener.headers:
                if re.match(pattern, self.opener.headers[header]):
                    return True
        return False

    @property
    def opener(self):
        """
        Returns the protected attribute opener
        :return: object
        """
        return self._session

    def update_headers(self, new_headers: dict):
        """
        Updates the context headers with the given ones.

        :param new_headers: dict
        """
        self.opener.headers.update(new_headers)

    def _get_default_headers(self):
        """
        Sets request headers based on different modes
        :return dict
        """
        headers = dict()

        headers["User-Agent"] = self._agent
        headers["Accept"] = self._accept
        headers["Accept-Language"] = self._lang
        headers["Connection"] = "keep-alive"
        headers["Referer"] = self._referer

        return headers

    def open_request(
            self,
            url='',
            post_fields=None,
            timeout=None):
        """
        Opens request and returns response.
        If parameter opener is not empty opens by urlopen else opens by opener.
        HTTP request will be a POST instead of a GET when the data parameter is
        provided.

        :param url: string url
        :param post_fields: dict post data fields, if it's none the used method
        :param timeout: int connection timeout

        :raise HTTPError
        :raise URLError
        :raise Exception
        :return HTTP Response
        """

        if not url:
            url = self._host

        try:

            if post_fields:
                if self._is_content_type_json():
                    post_fields = json.dumps(post_fields)
                response = self.opener.post(
                    url,
                    data=post_fields,
                    timeout=timeout,
                    verify=self._verify,
                    **self._req_kwargs
                )

            else:
                response = self.opener.get(
                    url,
                    timeout=timeout,
                    verify=self._verify,
                    **self._req_kwargs
                )

        except urllib3.exceptions.HTTPError:
            raise

        except Exception:
            raise

        return response

    @classmethod
    def _filter_no_post_url_kwargs(cls, kwargs):
        """
        Method urllib3.request.RequestMethods#request_encode_body has some
        not accessible function parameters that I'm passing through the url
        keyword arguments. There is any parameters of those that causes
        conflicts when the request method call is not POST. This little ugly
        filter is the best way I can remove those conflicts.
        :param kwargs: kwargs
        """
        if 'encode_multipart' in kwargs:
            del kwargs['encode_multipart']

    @classmethod
    def _parse_charset(cls, response):
        """
        Parses charset by the given HTTP response. Returns utf-8 as default.
        :return: str
        """
        default = "utf-8"
        possibles = [
            "Content-Type",
            "Content-type",
            "content-type"
        ]

        while possibles:
            search = possibles.pop()

            if search in response.headers:
                content_type = response.headers[search]
                match = re.match(
                    ".*charset=([^;]*)",
                    content_type,
                    re.IGNORECASE
                )
                if match:
                    return match.group(1)

        return default

    @classmethod
    def read_response(cls, response):
        """
        Gets page content by url
        :param response: HTTP Response
        :return: string
        """
        charset = cls._parse_charset(response)
        try:
            content = response.content.decode(charset)

        except UnicodeDecodeError:
            content = response.content

        except Exception:
            raise

        return content
