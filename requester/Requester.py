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
from http.cookies import _CookiePattern, Morsel, _unquote
from urllib.parse import urljoin


class LoaderCookie(cookieslib.SimpleCookie):
    """
    With Python 3.5.1 the cookies module does not load the cookies properly in
    one important scrapping case due to a comma appended after HttpOnly
    parameter.
    """

    def load(self, rawdata):
        super().load(rawdata)

        if rawdata and not self.output():
            if isinstance(rawdata, str):
                self.__parse_string(rawdata)
            else:
                # self.update() wouldn't call our custom __setitem__
                for key, value in rawdata.items():
                    self[key] = value

    def __set(self, key, real_value, coded_value):
        """Private method for setting a cookie's value"""
        M = self.get(key, Morsel())
        M.set(key, real_value, coded_value)
        dict.__setitem__(self, key, M)

    def __parse_string(self, str, patt=_CookiePattern):
        i = 0                 # Our starting point
        n = len(str)          # Length of string
        parsed_items = []     # Parsed (type, key, value) triples
        morsel_seen = False   # A key=value pair was previously encountered

        TYPE_ATTRIBUTE = 1
        TYPE_KEYVALUE = 2

        # We first parse the whole cookie string and reject it if it's
        # syntactically invalid (this helps avoid some classes of injection
        # attacks).
        while 0 <= i < n:
            # Start looking for a cookie
            match = patt.match(str, i)
            if not match:
                # No more cookies
                break

            key, value = match.group("key"), match.group("val")
            key = key.strip(',')        # Fix for httponly
            i = match.end(0)

            if key[0] == "$":
                if not morsel_seen:
                    # We ignore attributes which pertain to the cookie
                    # mechanism as a whole, such as "$Version".
                    # See RFC 2965. (Does anyone care?)
                    continue
                parsed_items.append((TYPE_ATTRIBUTE, key[1:], value))
            elif key.lower() in Morsel._reserved:
                if not morsel_seen:
                    # Invalid cookie string
                    return
                if value is None:
                    if key.lower() in Morsel._flags:
                        parsed_items.append((TYPE_ATTRIBUTE, key, True))
                    else:
                        # Invalid cookie string
                        return
                else:
                    parsed_items.append((TYPE_ATTRIBUTE, key, _unquote(value)))
            elif value is not None:
                parsed_items.append((TYPE_KEYVALUE, key, self.value_decode(value)))
                morsel_seen = True
            else:
                # Invalid cookie string
                return

        # The cookie string is valid, apply it.
        M = None         # current morsel
        for tp, key, value in parsed_items:
            if tp == TYPE_ATTRIBUTE:
                assert M is not None
                M[key] = value
            else:
                assert tp == TYPE_KEYVALUE
                rval, cval = value
                self.__set(key, rval, cval)
                M = self[key]


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

        self._configure_opener(force_ssl=force_ssl)

        self._cookies = LoaderCookie()

        pass

    @property
    def opener(self):
        """
        Returns the protected attribute opener
        :return: object
        """
        return self._opener

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
                self._filter_no_post_url_kwargs(kwargs)
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
        cookie_header = ""
        default_separator = "; "
        separator = ""
        response_cookies = response.getheader('set-cookie')
        if not response_cookies:
            return
        self._cookies.load(response_cookies)
        for cookie_name, cookie in self._cookies.items():
            cookie_header += "{!s}{!s}={!s}".format(
                separator,
                cookie_name,
                # why first cookie always ends with a comma
                cookie.coded_value.strip(",")
            )
            separator = default_separator
        self._headers['Cookie'] = cookie_header.strip()

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
