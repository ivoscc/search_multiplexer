# -*- coding: utf-8 -*-

import string
from urllib import urlencode
from itertools import count
from functools import partial

import tornado.ioloop
import tornado.web
from tornado import escape
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

allowed_chars = u''.join(((
    string.ascii_letters,
    string.digits,
    u" _.-*?@áéíóúñÁÉÍÓÚÑ+"
))).encode("utf-8")


class SearchHandler(tornado.web.RequestHandler):

    # holds the responses for api 
    response = {'posts': {}}

    def __init__(self, *args, **kwargs):
        self.api_url = kwargs.pop("api_url")
        super(SearchHandler, self).__init__(*args, **kwargs)

    def write(self, data):
        if self.jsonp_callback:
            data = "{0}({1})".format(self.jsonp_callback, data)
        super(SearchHandler, self).write(data)

    def _clean_term(self, term):
        """Returns the term with the allowed characters only."""
        return filter(lambda char: char in allowed_chars, term)

    def _handle_request(self, search_type, response):
        if response.error:
            self.response[search_type] = {}
        else:
            try:
                self.response[search_type] = escape.json_decode(response.body)
            except:
                self.response[search_type] = {}
        if self.counter.next() == len(self.response):
            self.write(escape.json_encode(self.response))
            self.finish()

    def _empty_answer(self):
        self.write(escape.json_encode(self.response))
        self.finish()

    @tornado.web.asynchronous
    def get(self):
        """Performs a search for each one of the services simultaneously."""

        self.counter = count(1)
        arguments = {}
        for arg_name in ('term', 'page', 'page_width', 'callback'):
            arg_value = self.get_argument(arg_name, None, True)
            if arg_value is not None:
                arguments[arg_name] = arg_value.encode('utf-8')

        self.jsonp_callback = arguments.pop('callback', None)

        if 'term' not in arguments:
            return self._empty_answer()
        arguments['term'] = self._clean_term(arguments['term'])
        if not arguments['term']:
            return self._empty_answer()

        http_client = AsyncHTTPClient()
        url = "{0}/{1}/?{2}"
        for search_type in self.response.keys():
            request = HTTPRequest(
                url.format(self.api_url, search_type, urlencode(arguments)),
                method='GET',
                request_timeout=3,
            )
            http_client.fetch(
                request,
                callback=partial(self._handle_request, search_type)
            )
