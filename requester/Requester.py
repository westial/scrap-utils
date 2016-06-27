#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Transmission class
#
from __future__ import absolute_import

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
                 force_ssl=None):
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

        if not agent:
            self._agent = self.DEFAULT_AGENT

        if not referer:
            self._referer = self.DEFAULT_REFERER

        if not accept:
            self._accept = self.DEFAULT_ACCEPT

        if not lang:
            self._lang = self.DEFAULT_LANG

        self._headers = self._get_default_headers()

        self._opener = None

        self._cookies = dict()

        self._verify = not force_ssl

        pass

    @property
    def opener(self):
        """
        Returns the protected attribute opener
        :return: object
        """
        return self

    def update_headers(self, new_headers: dict):
        """
        Updates the context headers with the given ones.

        :param new_headers: dict
        """
        self._headers.update(new_headers)

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
            timeout=None,
            allow_redirects=True):
        """
        Opens request and returns response.
        If parameter opener is not empty opens by urlopen else opens by opener.
        HTTP request will be a POST instead of a GET when the data parameter is
        provided.

        :param allow_redirects:
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
                response = requests.post(
                    url,
                    data=post_fields,
                    timeout=timeout,
                    headers=self._headers,
                    cookies=self._cookies,
                    allow_redirects=allow_redirects,
                    verify=self._verify
                )

            else:
                response = requests.get(
                    url,
                    timeout=timeout,
                    headers=self._headers,
                    cookies=self._cookies,
                    allow_redirects=allow_redirects,
                    verify=self._verify
                )

            self._update_headers(url, response)

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

    def _update_headers(self, referer, response):
        """
        Prepares headers for next request with the last response
        :param referer: str
        :param response: HTTP Response
        :return:
        """
        self._set_referer(referer)
        self._set_cookies(response)

    def _set_cookies(self, response):
        """
        Sets cookies on context opener for the given response.
        :param response: HTTP Response
        """
        self._cookies.update(response.cookies)

    def _set_referer(self, referer):
        """
        Sets referer to headers for next request.
        :param referer: str
        """
        self._headers['Referer'] = referer

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

        except Exception:
            raise

        return content
