#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Transmission class
#

import urllib
import urllib2
import cookielib


class Requester:
    """
    Transmission class.
    Used statically to open and read pages.
    Used as instance to login and bid managing cookies.
    :param host: string
    :param agent: string
    """

    DEFAULT_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130' \
                    '401 Firefox/31.0'

    DEFAULT_REFERER = 'https://www.google.com'

    DEFAULT_ACCEPT = 'application/json, text/plain, */*'

    def __init__(self, host, agent=None, referer=None, accept=None):

        self._host = host
        self._agent = agent
        self._referer = referer
        self._accept = accept

        if not host:
            raise ValueError('Host is mandatory')

        if not agent:
            self._agent = self.DEFAULT_AGENT

        if not referer:
            self._referer = self.DEFAULT_REFERER

        if not accept:
            self._accept = self.DEFAULT_ACCEPT

        self._opener = None         # OpenerDirector
        self._cookie_jar = None     # CookieJar
        self._headers = None

        self.request_headers()

        self._set_cookie_jar()

        pass

    @property
    def opener(self):
        """
        Returns the protected attribute opener
        :return: object
        """
        return self._opener

    @property
    def headers(self):
        """
        Returns the protected attribute headers
        :return: object
        """
        return self._headers

    @headers.setter
    def headers(self, value):
        """
        Sets the protected attribute headers

        :param value: list
        :return: object
        """
        self._headers = value
        pass

    def request_headers(self):
        """
        Sets request headers based on different modes
        :return list<tuple>
        """

        self._headers = [
            ("Host", self._host),
            ("User-Agent", self._agent),
            ("Accept", self._accept),
            ("Accept-Language", "en-US,en;q=0.5"),
            ("Connection", "keep-alive"),
            ("Pragma", "no-cache"),
            ("Cache-Control", "no-cache"),
            ("Referer", self._referer)]

        return

    def _set_cookie_jar(self):
        """
        Initializes _cookie_jar and _opener for a persistent session.
        """
        self._cookie_jar = cookielib.CookieJar()
        self._opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self._cookie_jar))
        self._opener.addheaders = self._headers

    def open_request(self, request, post_fields=None, timeout=None):
        """
        Opens request and returns response.
        If parameter opener is not empty opens by urlopen else opens by opener.
        HTTP request will be a POST instead of a GET when the data parameter is
        provided.

        :param request: string url
        :param post_fields: dict post data fields, if it's none the used method
        :param timeout: int
        will be get.

        :raise HTTPError
        :raise URLError
        :raise Exception
        :return HTTP Response
        """
        if post_fields is not None:
            data = urllib.urlencode(post_fields)
        else:
            data = post_fields

        try:
            response = self.opener.open(request, data, timeout)

        except urllib2.HTTPError:
            raise

        except urllib2.URLError:
            raise

        except Exception:
            raise

        return response

    @classmethod
    def read_response(cls, response):
        """
        Gets page content by url
        :param response: HTTP Response
        :return: string
        """
        try:
            content = response.read()

        except Exception:
            raise

        return content
