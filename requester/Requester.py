#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Transmission class
#
from __future__ import absolute_import

import re
import urllib3
import certifi

from http import cookies as cookieslib
from urllib.parse import urljoin


class Requester:
    """
    Transmission class.
    """

    DEFAULT_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130' \
                    '401 Firefox/31.0'

    DEFAULT_REFERER = 'http://www.westial.com'

    DEFAULT_ACCEPT = 'Accept=text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

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

        self._configure_opener(force_ssl=force_ssl)

        self._cookies = cookieslib.SimpleCookie()

        pass

    @property
    def opener(self):
        """
        Returns the protected attribute opener
        :return: object
        """
        return self._opener

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
        headers["Cache-Control"] = "max-age=0"
        headers["Referer"] = self._referer

        return headers

    def _configure_opener(self, force_ssl=False):
        """
        Initializes _cookie_jar and _opener for a persistent session.

        :param force_ssl: Adds a handler supporting unverified ssl certificate
        """

        if force_ssl:
            self._opener = urllib3.PoolManager(
                cert_reqs='CERT_NONE',
                assert_hostname=False
            )
            urllib3.disable_warnings()

        else:
            self._opener = urllib3.PoolManager(
                cert_reqs='CERT_REQUIRED',
                ca_certs=certifi.where()
            )

    def open_request(
            self,
            url='',
            post_fields=None,
            timeout=None,
            redirect_reuse=None,
            **kwargs):
        """
        Opens request and returns response.
        If parameter opener is not empty opens by urlopen else opens by opener.
        HTTP request will be a POST instead of a GET when the data parameter is
        provided.

        :param url: string url
        :param post_fields: dict post data fields, if it's none the used method
        :param timeout: int connection timeout
        :param redirect_reuse: bool
        :param kwargs: keyword arguments

        :raise HTTPError
        :raise URLError
        :raise Exception
        :return HTTP Response
        """
        kwargs["redirect"] = False

        if not url:
            url = self._host

        if timeout:
            timeout_ = urllib3.Timeout(connect=timeout)
        else:
            timeout_ = None

        try:

            if post_fields:
                response = self.opener.request(
                    'POST',
                    url,
                    fields=post_fields,
                    timeout=timeout_,
                    headers=self._headers,
                    **kwargs
                )

            else:
                response = self.opener.request(
                    'GET',
                    url,
                    timeout=timeout_,
                    headers=self._headers,
                    **kwargs
                )

            self._update_headers(url, response)
            response = self._redirect_response(
                url,
                redirect_reuse,
                response,
                timeout=timeout,
                **kwargs
            )

        except urllib3.exceptions.HTTPError:
            raise

        except Exception:
            raise

        return response

    def _redirect_response(self, url, redirect_reuse, response, timeout=None,
                           **kwargs):
        """
        Overrides the urllib3 redirect because we need to reuse some headers
        of the last request and response, like the cookies.

        Returns the response after. If no redirect, returns the original
        response.

        :param url: str
        :param redirect_reuse: bool
        :param response: HTTP Response
        :return HTTP Response
        """
        redirect_location = redirect_reuse and response.get_redirect_location()

        if not redirect_location:
            return response

        # Support relative URLs for redirecting.
        redirect_location = urljoin(url, redirect_location)

        return self.open_request(
            redirect_location,
            post_fields=None,
            timeout=timeout,
            redirect_reuse=redirect_reuse,
            **kwargs
        )

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
        response_cookies = response.getheader('set-cookie')
        if not response_cookies:
            return
        self._cookies.load(response_cookies)
        self._headers['Cookie'] = self._cookies.output(attrs=[], header='').strip()

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
            content = response.data.decode(charset)

        except Exception:
            raise

        return content
